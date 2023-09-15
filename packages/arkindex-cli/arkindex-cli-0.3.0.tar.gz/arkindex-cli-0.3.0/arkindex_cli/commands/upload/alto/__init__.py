# -*- coding: utf-8 -*-
import csv
import errno
import itertools
import json
import logging
import re
from pathlib import Path
from typing import List, Optional, Union
from uuid import UUID

from apistar.exceptions import ErrorResponse
from arkindex import ArkindexClient
from lxml import etree as ET
from lxml import objectify
from rich.progress import Progress, track

from arkindex_cli.argtypes import URLArgument
from arkindex_cli.auth import Profiles
from arkindex_cli.commands.upload.alto.parser import AltoElement, RootAltoElement

REGEX_IMAGE_ID = re.compile(r"0+(\d+)")

logger = logging.getLogger(__name__)


def add_alto_parser(subcommands):
    gallica = subcommands.add_parser(
        "gallica",
        help="The images are on Gallica IIIF server.",
    )
    gallica.add_argument(
        "--metadata-file",
        help="CSV that contains the metadata related to the Gallica import.",
        required=True,
        type=Path,
    )
    gallica.add_argument(
        "--alto-namespace",
        help="Specify an Alto namespace to use.",
        required=False,
        type=str,
    )
    gallica.add_argument(
        "path",
        help="Path to a directory which contains ALTO XML documents. Defaults to the current working directory.",
        type=Path,
        default=Path.cwd(),
    )
    gallica.add_argument(
        "--iiif-base-url",
        help="Base URL for the IIIF images, which will be prepended to all source image file names.",
        type=URLArgument(allow_query=False),
        required=True,
    )
    gallica.add_argument(
        "--parent-id",
        help="UUID of a parent folder under which page elements will be created.",
        type=UUID,
        required=True,
    )
    gallica.add_argument(
        "--json-summary",
        help="Build a JSON file creation report for each parsed ALTO file.",
        action="store_true",
    )
    gallica.add_argument(
        "--skip-metadatas",
        help="Skipping Alto ID metadata publication speeds up a lot the execution time",
        action="store_true",
    )
    gallica.add_argument(
        "--worker-run-id",
        help="Worker Run used to publish elements and transcriptions in bulk. This is required to use bulk endpoints and speed up publication.",
        type=UUID,
    ),
    types = gallica.add_mutually_exclusive_group(required=True)
    types.add_argument(
        "--create-types",
        help="Create an element type in the Arkindex corpus for each element type in the ALTO files.",
        action="store_true",
    )
    types.add_argument(
        "--existing-types",
        help='Specify correspondences between element types in the Arkindex corpus and in the ALTO files. Format: --existing-types="alto_type:arkindex_type alto_type_2:arkindex_type_2"',
        type=str,
    )
    gallica.set_defaults(func=run_gallica)

    alto = subcommands.add_parser(
        "alto",
        description="Upload ALTO XML documents to Arkindex.",
        help="Upload ALTO XML documents to Arkindex.",
    )
    alto.add_argument(
        "--alto-namespace",
        help="Specify an Alto namespace to use.",
        required=False,
        type=str,
    )
    alto.add_argument(
        "path",
        help="Path to a directory which contains ALTO XML documents. Defaults to the current working directory.",
        type=Path,
        default=Path.cwd(),
    )
    alto.add_argument(
        "--iiif-base-url",
        help="Base URL for the IIIF images, which will be prepended to all source image file names.",
        type=URLArgument(allow_query=False),
        required=True,
    )
    alto.add_argument(
        "--parent-id",
        help="UUID of a parent folder under which page elements will be created.",
        type=UUID,
        required=True,
    )
    alto.add_argument(
        "--skip-metadatas",
        help="Skipping Alto ID metadata publication speeds up a lot the execution time",
        action="store_true",
    )
    alto.add_argument(
        "--worker-run-id",
        help="Worker Run used to publish elements and transcriptions in bulk. This is required to use bulk endpoints and speed up publication.",
        type=UUID,
    )
    alto.add_argument(
        "--dpi-x",
        help="Horizontal resolution of the image, in dots per inch, to be used for ALTO files using coordinates in tenths of millimeters.\n"
        "Strictly positive integer. Ignored for files using coordinates in pixels.",
        type=int,
    )
    alto.add_argument(
        "--dpi-y",
        help="Vertical resolution of the image, in dots per inch, to be used for ALTO files using coordinates in tenths of millimeters.\n"
        "Strictly positive integer. Ignored for files using coordinates in pixels.",
        type=int,
    )
    alto.add_argument(
        "--json-summary",
        help="Build a JSON file creation report for each parsed ALTO file.",
        action="store_true",
    )
    types = alto.add_mutually_exclusive_group(required=True)
    types.add_argument(
        "--create-types",
        help="Create an element type in the Arkindex corpus for each element type in the ALTO files.",
        action="store_true",
    )
    types.add_argument(
        "--existing-types",
        help='Specify correspondences between element types in the Arkindex corpus and in the ALTO files. Format: --existing-types="alto_type:arkindex_type alto_type_2:arkindex_type_2"',
        type=str,
    )
    alto.set_defaults(func=run)


def check_element_type(corpus: dict, type_slug: str) -> None:
    types = {type["slug"] for type in corpus["types"]}
    if type_slug not in types:
        raise ValueError(f"Type {type_slug} not found.")
    return True


def create_iiif_image(client: ArkindexClient, url: str) -> str:
    try:
        image = client.request("CreateIIIFURL", body={"url": url})
        return image["id"]
    except ErrorResponse as e:
        # When the image already exists, its ID is returned in a HTTP 400
        if e.status_code == 400 and "id" in e.content:
            return e.content["id"]
        raise


_TYPES = {}


def get_element_type(
    client: ArkindexClient,
    corpus_id: UUID,
    node_name: str,
    types_dict: Optional[dict],
    create_types: bool = False,
):
    """
    Retrieve or create an alto node's corresponding Arkindex element type.
    Always fetch types from Arkindex if not cached yet.
    If types_dict is set, directly look for a matching type from that dictionary.
    Otherwise, look for a matching Arkindex type, creating it if required.
    """
    corpus_id = str(corpus_id)
    if corpus_id not in _TYPES:
        _TYPES[corpus_id] = arkindex_corpus_types = [
            item["slug"]
            for item in client.request("RetrieveCorpus", id=corpus_id)["types"]
        ]
    else:
        arkindex_corpus_types = _TYPES[corpus_id]

    if types_dict is not None:
        if node_name not in types_dict:
            raise Exception(f"Alto element {node_name} not in given types dictionary.")
        else:
            return types_dict[node_name]
    elif create_types:
        if node_name not in arkindex_corpus_types:
            logger.info(
                f"Creating element type {node_name} in target corpus {corpus_id}…"
            )
            try:
                client.request(
                    "CreateElementType",
                    body={
                        "slug": node_name,
                        "display_name": node_name,
                        "corpus": corpus_id,
                    },
                )
                _TYPES[corpus_id].append(node_name)
            except ErrorResponse as e:
                logger.error(
                    f"Failed to create element type {node_name} in target corpus {corpus_id}."
                )
                raise Exception(e.content)
        else:
            logger.debug(
                f"Element type {node_name} exists in target corpus {corpus_id}."
            )
        return node_name
    raise ValueError(
        f"No type can be found matching node {node_name} in corpus {corpus_id}. "
        "Hint: either define types_dict or allow type creation."
    )


def create_elements(
    client: ArkindexClient,
    nodes: List[AltoElement],
    image_id: str,
    parent_id: UUID,
    corpus_id: UUID,
    worker_run_id: UUID,
    parent_node: Union[AltoElement, None] = None,
    publish_metadatas: bool = True,
    create_types: bool = True,
    types_dict: Optional[dict] = None,
):
    # Mapping of Alto ID => Arkindex ID
    out = {}

    # Cleanup nodes:
    # - no nodes without ID
    # - no nodes without polygon when parent has a polygon
    nodes = [
        node for node in nodes if node.id and (parent_node is None or node.polygon)
    ]
    if not nodes:
        return out

    # Create elements slowly one-by-one when
    # - parent is unknown, so probably without any polygon nor image
    # - parent is known but has not polygon
    # - all nodes without any zones
    # - no worker run ID is set
    distinctive_elts = [node for node in nodes if not node.polygon]
    if parent_node is None or not parent_node.polygon or not worker_run_id:
        distinctive_elts += nodes

    for node in distinctive_elts:
        body = {
            "corpus": str(corpus_id),
            "parent": str(parent_id),
            "type": get_element_type(
                client,
                corpus_id,
                node.node_name,
                types_dict=types_dict,
                create_types=create_types,
            ),
            "name": node.name,
        }

        if image_id and node.polygon:
            body["polygon"] = node.polygon
            body["image"] = image_id

        element = client.request(
            "CreateElement",
            body=body,
        )

        # Store the arkindex ID of the newly created element
        out[node.id] = element["id"]

        # Build transcription when available
        if node.text:
            client.request(
                "CreateTranscription",
                id=element["id"],
                body={"text": node.text},
            )

    if distinctive_elts:
        logger.info(f"Published {len(distinctive_elts)} elements distinctly")

    # Split remaining nodes with/without transcriptions
    # to take advantage of CreateElements & CreateElementTranscriptions
    with_transcriptions = [node for node in nodes if node.text and node.id not in out]
    without_transcriptions = [
        node for node in nodes if not node.text and node.id not in out
    ]

    if without_transcriptions:
        try:
            elements = client.request(
                "CreateElements",
                id=parent_id,
                body={
                    "worker_run_id": str(worker_run_id),
                    "elements": [
                        {
                            "name": node.name,
                            "type": get_element_type(
                                client,
                                corpus_id,
                                node.node_name,
                                types_dict=types_dict,
                                create_types=create_types,
                            ),
                            "polygon": node.polygon,
                        }
                        for node in without_transcriptions
                    ],
                },
            )
        except ErrorResponse as e:
            logger.error(f"Failed to create elements: {e.content}")
            raise

        # Store the arkindex ID of the newly created element
        node_ids = (node.id for node in without_transcriptions)
        arkindex_ids = (elt["id"] for elt in elements)
        out.update(dict(zip(node_ids, arkindex_ids)))

        logger.info(f"Published {len(without_transcriptions)} elements")

    if with_transcriptions:

        # To create elements and transcriptions, we first
        # need to group nodes by their types
        groups = itertools.groupby(
            sorted(with_transcriptions, key=lambda n: n.node_name),
            lambda n: n.node_name,
        )

        for node_name, node_group in groups:
            node_group = list(node_group)  # needed because we access it several times
            try:
                elements = client.request(
                    "CreateElementTranscriptions",
                    id=parent_id,
                    body={
                        "element_type": get_element_type(
                            client,
                            corpus_id,
                            node_name,
                            types_dict=types_dict,
                            create_types=create_types,
                        ),
                        "worker_run_id": str(worker_run_id),
                        "return_elements": True,
                        "transcriptions": [
                            {
                                "polygon": node.polygon,
                                "text": node.text,
                                "confidence": 1.0,
                            }
                            for node in node_group
                        ],
                    },
                )
            except ErrorResponse as e:
                logger.error(f"Failed to create elements: {e.content}")
                raise

            # Store the arkindex ID of the newly created element
            node_ids = (node.id for node in node_group)
            arkindex_ids = (elt["element_id"] for elt in elements)
            out.update(dict(zip(node_ids, arkindex_ids)))

        logger.info(
            f"Published {len(with_transcriptions)} elements with transcriptions"
        )

    # Publish metadatas slowly, there is no alternative here
    if publish_metadatas:
        for node in nodes:
            client.request(
                "CreateMetaData",
                id=out[node.id],
                body={"name": "Alto ID", "value": node.id, "type": "reference"},
            )

        logger.info(f"Published {len(nodes)} metadatas")

    # All nodes are created at this point
    # we can directly iterate on their children
    for node in nodes:
        if not node.children:
            continue

        out.update(
            create_elements(
                client,
                nodes=node.children,
                image_id=image_id,
                parent_id=out[node.id],
                corpus_id=corpus_id,
                worker_run_id=worker_run_id,
                parent_node=node,
                publish_metadatas=publish_metadatas,
                types_dict=types_dict,
                create_types=create_types,
            )
        )

    return out


def format_url(path: Path, iiif_base_url: str, folders_ark_id_dict: dict = None):
    """
    This function is used to create the url to get the image from the Gallica IIIF server
    """
    # The path.name looks like 18840615_1-0003.xml with the folder id being the 18840615 which we use to
    # find the ark_id in order to get the folder from the Gallica server in this case it is ark:/12148/bpt6k7155522
    # the image id is 3 which we add to the url to get the image within the folder on Gallica so this gives us ark:/12148/bpt6k7155522/f3
    # the final link will be http://gallica.bnf.fr/iiif/ark:/12148/bpt6k7155522/f1
    if "-" in path.name:
        basename = path.name.split("-")[1]
        file_extension = path.name.split("-")[0]
        folder_id = file_extension.split("_")[0]
    else:
        # path looks like <folder_id>/ocr/image_id.xml
        folder_id = str(path).split(sep="/")[0]
        basename = path.name
    image_id = basename.replace(".xml", "")
    ark_id = folders_ark_id_dict[folder_id]
    return f"{iiif_base_url}{ark_id}/f{parse_image_idx(image_id)}"


def parse_image_idx(image_id):
    # Remove leading 0s
    image_idx = REGEX_IMAGE_ID.search(image_id)
    assert image_idx, f"Could not parse the image IDX from `{image_id}`"
    return image_idx.group(1)


def upload_alto_file(
    path: Path,
    client: ArkindexClient,
    iiif_base_url: str,
    corpus: dict,
    parent_id: UUID,
    types_dict: Optional[dict],
    create_types: bool,
    dpi_x: Optional[int] = None,
    dpi_y: Optional[int] = None,
    gallica: bool = False,
    folders_ark_id_dict: dict = None,
    alto_namespace: str = None,
    json_summary: bool = False,
    worker_run_id: Optional[UUID] = None,
    skip_metadatas: bool = False,
) -> None:
    with open(path) as file:
        # This ensures that comments in the XML files do not cause the
        # "no Alto namespace found" exception.
        parser = ET.XMLParser(remove_comments=True)
        tree = objectify.parse(file, parser=parser)
        root = RootAltoElement(
            tree.getroot(), alto_namespace=alto_namespace, dpi_x=dpi_x, dpi_y=dpi_y
        )

    # Skip empty files immediately
    if not len(root.content):
        logger.warning(f"No content found in file {path}")
        return

    page_nodes = root.content.findall(".//{*}Page", namespaces=root.namespaces)
    if len(page_nodes) == 1:
        # We use + here and not urljoin or path.join to create image URLs
        # because the base URL could contain a portion of the identifier:
        # 'http://server/iiif/root%2Fdirectory'
        # urljoin or path.join would erase that identifier prefix.
        if gallica:
            url = format_url(path, iiif_base_url, folders_ark_id_dict)
            image_id = create_iiif_image(client, url)
        else:
            image_id = create_iiif_image(client, iiif_base_url + root.filename)
        page_node = AltoElement(
            page_nodes[0],
            alto_namespace=alto_namespace,
            unit=root.unit,
            dpi_x=dpi_x,
            dpi_y=dpi_y,
        )
        page_node.parse_children()
        elements = create_elements(
            client=client,
            nodes=[page_node],
            image_id=image_id,
            parent_id=parent_id,
            corpus_id=corpus["id"],
            worker_run_id=worker_run_id,
            publish_metadatas=not skip_metadatas,
            create_types=create_types,
            types_dict=types_dict,
        )
    elif len(page_nodes) > 1:
        elements = {}
        for page_node in page_nodes:
            page_node = AltoElement(
                page_node,
                alto_namespace=alto_namespace,
                unit=root.unit,
                dpi_x=dpi_x,
                dpi_y=dpi_y,
            )
            if page_node.page_image_id is None:
                logger.warning(
                    "Attribute PHYSICAL_IMG_NR was not set for this Page node. Skipping…"
                )
                return
            image_id = create_iiif_image(
                client, iiif_base_url + page_node.page_image_id
            )
            elements.update(
                create_elements(
                    client=client,
                    nodes=[page_node],
                    image_id=image_id,
                    parent_id=parent_id,
                    corpus_id=corpus,
                    worker_run_id=worker_run_id,
                    publish_metadatas=not skip_metadatas,
                    create_types=create_types,
                    types_dict=types_dict,
                )
            )
    else:
        logger.warning(f"No Page node found in file {root.filename}. Skipping…")
        return

    if json_summary:
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(
                {
                    "alto_file": str(path),
                    "arkindex_api_url": client.document.url,
                    "elements": elements,
                },
                f,
                sort_keys=True,
                indent=4,
            )


def run_gallica(
    path: Path,
    iiif_base_url: str,
    parent_id: UUID,
    create_types: bool = False,
    existing_types: Optional[str] = None,
    metadata_file: Path = None,
    json_summary: bool = False,
    profile_slug: Optional[str] = None,
    alto_namespace: str = None,
    worker_run_id: Optional[UUID] = None,
    skip_metadatas: bool = False,
):
    # If this is a Gallica import, load the metadata CSV file
    folders_ark_id_dict = dict()
    with open(metadata_file, "r") as file:
        reader = csv.reader(file)
        # Create a dictionary with the folder name as the id and the Gallica Ark ID as the value
        folders_ark_id_dict = {row[0]: row[1] for row in reader}
    run(
        path=path,
        iiif_base_url=iiif_base_url,
        parent_id=parent_id,
        create_types=create_types,
        existing_types=existing_types,
        folders_ark_id_dict=folders_ark_id_dict,
        gallica=True,
        profile_slug=profile_slug,
        alto_namespace=alto_namespace,
        json_summary=json_summary,
        worker_run_id=worker_run_id,
        skip_metadatas=skip_metadatas,
    )


def run(
    path: Path,
    iiif_base_url: str,
    parent_id: UUID,
    dpi_x: Optional[int] = None,
    dpi_y: Optional[int] = None,
    create_types: bool = False,
    existing_types: Optional[str] = None,
    folders_ark_id_dict: dict = None,
    profile_slug: Optional[str] = None,
    gallica: bool = False,
    alto_namespace: str = None,
    json_summary: bool = False,
    worker_run_id: Optional[UUID] = None,
    skip_metadatas: bool = False,
) -> int:
    if (dpi_x is None) ^ (dpi_y is None):
        logger.error("--dpi-x and --dpi-y must be either both set or both unset.")
        return errno.EINVAL

    if dpi_x is not None and dpi_x <= 0:
        logger.error("--dpi-x must be a strictly positive integer.")
        return errno.EINVAL

    if dpi_y is not None and dpi_y <= 0:
        logger.error("--dpi-y must be a strictly positive integer.")
        return errno.EINVAL

    if not path.is_dir():
        logger.error(f"{path} is not a directory.")
        return errno.ENOTDIR

    file_paths = list(path.rglob("*.xml"))
    if not file_paths:
        logger.error(f"No XML files found in {path}.")
        return errno.ENOENT

    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        client = Profiles().get_api_client_or_exit(profile_slug)

    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Fetching parent element")
        try:
            parent = client.request("RetrieveElement", id=parent_id)
        except ErrorResponse as e:
            logger.error(
                f"Could not retrieve parent element {parent_id}: HTTP {e.status_code} - {e.content}"
            )
            return errno.EREMOTEIO

    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Fetching corpus")
        corpus_id = parent["corpus"]["id"]
        try:
            corpus = client.request("RetrieveCorpus", id=corpus_id)
        except ErrorResponse as e:
            logger.error(
                f"Could not retrieve corpus {corpus_id}: HTTP {e.status_code} - {e.content}"
            )
            return errno.EREMOTEIO

    if not worker_run_id:
        logger.info(
            "Upload METS in slow mode (Set --worker-run-id to use bulk endpoints)"
        )

    types_dict = None
    if existing_types:
        split_str = existing_types.split(" ")
        types_dict = {}
        for item in split_str:
            split_item = item.split(":")
            types_dict[str(split_item[0]).lower()] = str(split_item[1]).lower()
        for key, arkindex_type in types_dict.items():
            try:
                check_element_type(corpus, arkindex_type)
            except ValueError as e:
                logger.error(str(e))
                return errno.EINVAL

    failed = 0

    for file_path in track(file_paths, description="Uploading"):
        try:
            upload_alto_file(
                gallica=gallica,
                folders_ark_id_dict=folders_ark_id_dict,
                path=file_path,
                client=client,
                iiif_base_url=iiif_base_url,
                corpus=corpus,
                parent_id=parent_id,
                types_dict=types_dict,
                create_types=create_types,
                dpi_x=dpi_x,
                dpi_y=dpi_y,
                alto_namespace=alto_namespace,
                json_summary=json_summary,
                worker_run_id=worker_run_id,
                skip_metadatas=skip_metadatas,
            )
        except ErrorResponse as e:
            logger.error(
                f"Upload failed for file {file_path}: HTTP {e.status_code} - {e.content}"
            )
            failed += 1
        except Exception as e:
            logger.error(f"Upload failed for file {file_path}: {e}")
            failed += 1
    # Return a non-zero error code when all files have failed
    return failed >= len(file_paths)
