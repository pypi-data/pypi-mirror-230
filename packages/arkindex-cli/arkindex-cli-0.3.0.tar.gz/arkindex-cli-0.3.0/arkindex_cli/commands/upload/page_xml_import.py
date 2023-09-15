# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path
from typing import Optional
from uuid import UUID

from apistar.exceptions import ErrorResponse
from rich.progress import Progress
from transkribus.pagexml import PageXmlPage

from arkindex_cli.auth import Profiles

logger = logging.getLogger(__name__)


class PageXmlParser(object):
    def __init__(self, client, path_or_xml):
        self.pagexml_page = PageXmlPage(path_or_xml)
        self.client = client

    def check_element(self, region):
        """
        checks if the element's polygon contains enough points to create a transcription on it
        and returns the points
        check if all coordinates are positive, clip to 0 otherwise
        """
        points = region.points
        region_id = region.id
        if points is None:
            logger.warning(f"No points in region {region_id}")
            return
        if len(points) < 3:
            logger.warning(
                f"Ignoring region {region_id} (not enough points in polygon)"
            )
            return
        points = [(max(0, x), max(0, y)) for x, y in points]
        return points

    def save_element(self, corpus_id, parent_id, image_id, name, points, elt_type):
        """
        creates an element for a given text region in order to create a transcription
        on that element
        """
        try:
            element = self.client.request(
                "CreateElement",
                body={
                    "type": elt_type,
                    "name": name,
                    "corpus": corpus_id,
                    "parent": parent_id,
                    "image": image_id,
                    "polygon": points,
                },
            )
            return element
        except ErrorResponse as e:
            logger.error(f"Failed in creating element {e.status_code} - {e.content}")
            return None

    def save_transcription(self, region, element):
        """
        create a transcription on an element
        """
        logger.debug(f"Creating transcription for element {element['name']}...")
        try:
            self.client.request(
                "CreateTranscription",
                id=element["id"],
                body={
                    "text": region.text,
                    "worker_version": None,
                    "confidence": 1,
                },
            )
        except ErrorResponse as e:
            logger.error(
                f"Failed in creating transcription {e.status_code} - {e.content}"
            )

    def save(self, element, image_id):
        region_count, element_ts_count = 0, 0
        for region in self.pagexml_page.page.text_regions:
            points = self.check_element(region)
            if points is None:
                continue
            if region.type == "paragraph":
                elt_type = "paragraph"
            else:
                elt_type = "text_zone"
            try:
                region_element = self.save_element(
                    corpus_id=element["corpus"]["id"],
                    parent_id=element["id"],
                    image_id=image_id,
                    name=str(region_count),
                    points=points,
                    elt_type=elt_type,
                )
                if region_element:
                    region_count += 1
                    self.save_transcription(region=region, element=region_element)
                    element_ts_count += 1
                    logger.info(
                        f"Created element {region_element['id']} and its transcription"
                    )
                else:
                    logger.error(
                        "Could not create a transcription on the element because element creation failed"
                    )
                    continue
            except ErrorResponse as e:
                logger.error(
                    f"Failed in creating element {e.status_code} - {e.content}"
                )

            for line in region.lines:
                points = self.check_element(line)
                if points is None:
                    continue
                try:
                    line_element = self.save_element(
                        corpus_id=element["corpus"]["id"],
                        parent_id=region_element["id"],
                        image_id=image_id,
                        name=str(region_count),
                        points=points,
                        elt_type="text_line",
                    )
                    if line_element:
                        region_count += 1
                        self.save_transcription(region=line, element=line_element)
                        element_ts_count += 1
                        logger.info(
                            f"Created line element {line_element['id']} and its transcription"
                        )
                    else:
                        logger.error(
                            "Could not create a transcription on the element because element creation failed"
                        )
                        continue
                except ErrorResponse as e:
                    logger.error(
                        f"Failed in creating element {e.status_code} - {e.content}"
                    )

        logger.info(
            f"Parsed {region_count} regions and created {element_ts_count} elements with a transcription."
        )


def add_pagexml_import_parser(subcommands):
    pagexml_import_parser = subcommands.add_parser(
        "pagexml",
        description="Upload PAGE-XML transcriptions to images on Arkindex.",
        help="Upload PAGE-XML transcriptions to images on Arkindex.",
    )
    pagexml_import_parser.add_argument(
        "--xml-path",
        type=Path,
        help="the path of the folder containing the xml files or the file containing the paths to the xml files",
        required=True,
    )
    pagexml_import_parser.add_argument(
        "--parent",
        help="UUID of an existing parent element for all the imported data",
        type=UUID,
        required=True,
    )
    pagexml_import_parser.set_defaults(func=run)


def run(
    parent: UUID,
    xml_path: Optional[Path] = None,
    profile_slug: Optional[str] = None,
) -> int:
    """
    Push PAGE-XML transcriptions on Arkindex
    """
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        profiles = Profiles()
        profile = profiles.get_or_exit(profile_slug)
        client = profiles.get_api_client(profile)

    if xml_path.is_dir():
        files = [f for f in xml_path.glob("*.xml")]
    elif xml_path.is_file():
        files = [f.strip() for f in xml_path.read_text().splitlines()]
    else:
        logger.error(f"path {xml_path} doesn't exist")
    if len(files) == 0:
        logger.error("No files are specified")
        return
    for f in files:
        parser = PageXmlParser(client, f)
        arkindex_name = parser.pagexml_page.page.image_name
        if not arkindex_name:
            logger.error(f"No image name for file {f}")
            continue
        arkindex_name = os.path.splitext(arkindex_name)[0]
        logger.info(f"pushing annotations for page {arkindex_name}")
        found = False
        try:
            for p in client.paginate(
                "ListElementChildren",
                id=parent,
                type="page",
                name=arkindex_name,
                recursive=True,
            ):
                if arkindex_name == p["name"]:
                    parser.save(element=p, image_id=p["zone"]["image"]["id"])
                    found = True
                    break
            if not found:
                logger.error(
                    f"a page with the name {arkindex_name} was not found on Arkindex"
                )

        except ErrorResponse as e:
            logger.error(f"Failed in retrieving page {e.status_code} - {e.content}")
