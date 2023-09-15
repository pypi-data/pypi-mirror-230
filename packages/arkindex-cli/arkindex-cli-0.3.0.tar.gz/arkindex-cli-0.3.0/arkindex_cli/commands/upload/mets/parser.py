# -*- coding: utf-8 -*-
import logging
import urllib.parse
from pathlib import Path

from apistar.exceptions import ErrorResponse
from lxml import etree as ET
from lxml import objectify

from arkindex_cli.commands.upload.alto import create_elements, create_iiif_image
from arkindex_cli.commands.upload.alto.parser import AltoElement, RootAltoElement
from arkindex_cli.commands.upload.mets.cache import Cache

logger = logging.getLogger(__name__)

# Only need METS base support here
METS_NS = {"mets": "http://www.loc.gov/METS/", "xlink": "http://www.w3.org/1999/xlink"}

IMAGE_SUFFIXES = (".jpeg", ".jpg", ".png", ".tiff", ".tif")
ALTO_SUFFIXES = (".xml",)


class MetsProcessingError(Exception):
    """
    Raised when there has been an error in the Mets upload processing
    """


class MetsImage(object):
    """
    A remote IIIF image
    """

    def __init__(self, image_relative_path, iiif_base_url, iiif_prefix):
        # Build IIIF url for the image
        # knowing only its relative path to the folder with METS file
        image_path = urllib.parse.urljoin(iiif_prefix, image_relative_path)
        self.url = iiif_base_url + urllib.parse.quote_plus(image_path)

        self.cache_key = f"image/{image_relative_path}"

    def publish(self, arkindex_client):

        # Check cache
        self.arkindex_id = Cache.get(self.cache_key)
        if self.arkindex_id is not None:
            return

        # Declare image on Arkindex
        self.arkindex_id = create_iiif_image(arkindex_client, self.url)
        logger.info(f"Published image {self.arkindex_id}")

        # Store in cache
        Cache.set(self.cache_key, self.arkindex_id)


class MetsAlto(object):
    """
    A local ALTO XML file
    """

    def __init__(self, path, dpi_x=None, dpi_y=None):
        self.path = path

        with open(path) as file:
            # This ensures that comments in the XML files do not cause the
            # "no Alto namespace found" exception.
            parser = ET.XMLParser(remove_comments=True)
            tree = objectify.parse(file, parser=parser)
            self.root = RootAltoElement(tree.getroot(), dpi_x=dpi_x, dpi_y=dpi_y)

    def __eq__(self, other):
        # Used in unit tests to compare 2 instances
        return self.path.absolute() == other.path.absolute()

    def parse(self, target_id):
        self.target_id = target_id
        self.cache_key = f"alto/{self.path}/{self.target_id}"

        # Find element matching provided id
        xpath = f".//*[@ID='{target_id}']"
        xml_target = self.root.content.find(xpath)
        if xml_target is None:
            return

        # Parse ALTO file down that element
        self.element = AltoElement(
            xml_target,
            unit=self.root.unit,
            dpi_x=self.root.dpi_x,
            dpi_y=self.root.dpi_y,
        )
        self.element.parse_children()

    def publish(
        self,
        arkindex_client,
        corpus_id,
        parent_id=None,
        image=None,
        worker_run_id=None,
        publish_metadatas=True,
    ):
        # Check cache
        arkindex_id = Cache.get(self.cache_key)
        if arkindex_id is not None:

            # Create parent link
            if parent_id is not None:
                try:
                    arkindex_client.request(
                        "CreateElementParent",
                        child=arkindex_id,
                        parent=parent_id,
                    )
                except ErrorResponse as e:
                    # link already exists when 400 is received
                    if e.status_code != 400:
                        raise Exception(
                            f"Failed to create placeholder element: {e.content}"
                        )

            return arkindex_id

        image_id = image.arkindex_id if image is not None else None
        try:
            elements = create_elements(
                client=arkindex_client,
                nodes=[
                    self.element,
                ],
                image_id=image_id,
                corpus_id=str(corpus_id),
                parent_id=parent_id,
                worker_run_id=worker_run_id,
                publish_metadatas=publish_metadatas,
            )

        except ErrorResponse as e:
            logger.info(f"Failed to create elements: {e.content}")
            raise

        # ALTO processor builds Arkindex elements
        # and returns a mapping of ALTO ID => Arkindex ID
        assert (
            self.target_id in elements
        ), f"Missing ALTO element {self.target_id} in arkindex elements"

        # Store in cache all elements
        for key, value in elements.items():
            Cache.set(f"alto/{self.path}/{key}", value)

        return elements[self.target_id]


class MetsElement:
    def __init__(self, node, parent=None) -> None:
        self.node = node
        self.parent = parent

        # Populated during publication on Arkindex
        self.arkindex_id = None

    @property
    def parent_id(self):
        if self.parent is None:
            return
        return self.parent.arkindex_id

    @property
    def type(self):
        if self.node is None:
            return "folder"
        return self.node.attrib["TYPE"]

    @property
    def id(self):
        if self.node is None:
            return "ROOT"
        return self.node.attrib["ID"]

    @property
    def label(self):
        if self.node is None:
            return "METS Import"
        return self.node.attrib.get("LABEL", self.id)[:250]

    def publish(self, arkindex_client, corpus_id):
        """
        Publish elements not linked to an image: every element mentioned in METS
        that is not described by an ALTO file
        """
        # Check cache
        cache_key = f"mets/{self.id}"
        self.arkindex_id = Cache.get(cache_key)
        if self.arkindex_id is not None:
            return self.arkindex_id

        # Publish element without any link to an image
        try:
            logger.info(f"Creating {self.type} {self.label}…")
            resp = arkindex_client.request(
                "CreateElement",
                body={
                    "name": self.label,
                    "type": self.type,
                    "corpus": str(corpus_id),
                    "parent": self.parent_id and str(self.parent_id) or None,
                },
            )
        except ErrorResponse as e:
            raise Exception(f"Failed to create placeholder element: {e.content}")

        self.arkindex_id = resp["id"]

        # Publish METS ID as metadata for later reference
        logger.info(f"Storing METS ID as metadata on {self.arkindex_id}…")
        try:
            arkindex_client.request(
                "CreateMetaData",
                id=self.arkindex_id,
                body={
                    "name": "METS ID",
                    "value": self.id,
                    "type": "reference",
                },
            )

        except ErrorResponse as e:
            logger.error(
                f"Could not create metadata on element ({self.arkindex_id}): HTTP {e.status_code} - {e.content}"
            )
            raise MetsProcessingError

        # Store arkindex reference in cache
        Cache.set(cache_key, self.arkindex_id)


class RootMetsElement(object):
    def __init__(self, path, iiif_base_url, iiif_prefix=None, dpi_x=None, dpi_y=None):
        self.files_mapping = {}
        """Mapping from file_ids (as defined in the METS) to tuple of
        - path to ALTO xml file,
        - Loaded Arkindex summary.
        """

        with path.open() as file:
            # This ensures that comments in the XML files do not cause the
            # "no Alto namespace found" exception.
            parser = ET.XMLParser(remove_comments=True)
            tree = objectify.parse(file, parser=parser)
            self.root = tree.getroot()

        self.iiif_base_url = iiif_base_url
        self.iiif_prefix = iiif_prefix
        self.dpi_x = dpi_x
        self.dpi_y = dpi_y
        self.parse_files(path)

    def parse_files(self, toc_file: Path):
        """
        Parse files listed in the METS file section,
        and extract its immediate child FLocat path
        and build a relevant high-level class to use the content of
        - remote images
        - local Alto file
        """

        # Iterate over <file> in any <filesec>
        for file in self.root.xpath(
            "./mets:fileSec/mets:fileGrp/mets:file", namespaces=METS_NS
        ):

            try:
                location = file.find("mets:FLocat", namespaces=METS_NS)
                assert (
                    location is not None
                ), f"Could not find location of file ({file.get('ID')}) in METS."
                href = location.get("{" + METS_NS["xlink"] + "}href")

                # Only support local files for now
                if href.startswith("file://"):
                    href = href[7:]
                file_path = (toc_file.parent / href).resolve()

                mime_type = file.attrib.get("MIMETYPE")
            except AssertionError as e:
                logger.error(
                    f"Could not parse file {file} ({file.get('ID')}): {str(e)}"
                )
                raise MetsProcessingError

            # Build IIIF image using local path to an image (even when not present)
            if (
                mime_type and mime_type.startswith("image/")
            ) or file_path.suffix.lower() in IMAGE_SUFFIXES:
                relpath = str(file_path.relative_to(toc_file.parent.resolve()))
                self.files_mapping[file.attrib["ID"]] = MetsImage(
                    relpath,
                    self.iiif_base_url,
                    self.iiif_prefix,
                )

            # Local Alto file
            elif (
                mime_type and mime_type == "text/xml"
            ) or file_path.suffix.lower() in ALTO_SUFFIXES:
                self.files_mapping[file.attrib["ID"]] = MetsAlto(
                    file_path, self.dpi_x, self.dpi_y
                )

            else:
                logger.warning(f"Unsupported file {file_path}")

    def list_required_types(self):
        # each <div> with a type will generate a new arkindex element
        return set(
            self.root.xpath("./mets:structMap//mets:div/@TYPE", namespaces=METS_NS)
        )

    def publish(
        self,
        arkindex_client,
        parent_id,
        corpus_id,
        worker_run_id=None,
        publish_metadatas=True,
    ):
        """Build the hierarchy on Arkindex, browsing the tree in a breadth-first fashion

        :param arkindex_client: Arkindex API client.
        :param parent_id: Root element id on Arkindex.
        :param corpus_id: ID of the corpus where the element will be created
        """
        # Mock top element as it's already present in Arkindex and
        # has no real presence in the METS file
        top = MetsElement(None)
        top.arkindex_id = parent_id

        # Find all structure maps and process their children
        for div in self.root.xpath("./mets:structMap/mets:div", namespaces=METS_NS):

            # Convert XML node to MetsElement, linked to our top element
            element = MetsElement(div, parent=top)
            logger.info(f"Build {element.type} {element.id} : {element.label}")

            self.publish_element(
                arkindex_client, corpus_id, element, worker_run_id, publish_metadatas
            )

    def publish_element(
        self,
        arkindex_client,
        corpus_id,
        element: MetsElement,
        worker_run_id=None,
        publish_metadatas=True,
    ):
        """
        Recursive method that process a METS structural node
        and publishes relevant parts on Arkindex (image or elements)
        """
        # Simple discovery algo where we only remember the first alto & image found
        data, images = [], []
        image = None
        for area in element.node.findall("./mets:fptr//mets:area", namespaces=METS_NS):
            file = self.files_mapping.get(area.attrib["FILEID"])
            if file is None:
                continue
            if isinstance(file, MetsAlto):
                alto = file
                alto_begin = area.attrib.get("BEGIN")
                data.append((alto, alto_begin))
            elif isinstance(file, MetsImage):
                images.append(file)

        if images:
            # There should be only one image
            assert len(images) == 1
            image = images.pop()

        if not data:
            # Simply create a placeholder element
            element.publish(arkindex_client, corpus_id)
        else:
            for alto, alto_begin in data:
                # Parse then publish on Arkindex
                alto.parse(alto_begin)

                # Publish IIIF image
                if image:
                    image.publish(arkindex_client)

                # Store arkindex id on element
                element.arkindex_id = alto.publish(
                    arkindex_client,
                    corpus_id,
                    element.parent_id,
                    image,
                    worker_run_id,
                    publish_metadatas,
                )

        # Recursion
        for child in element.node.findall("./mets:div", namespaces=METS_NS):
            child_element = MetsElement(child, parent=element)
            self.publish_element(
                arkindex_client,
                corpus_id,
                child_element,
                worker_run_id,
                publish_metadatas,
            )
