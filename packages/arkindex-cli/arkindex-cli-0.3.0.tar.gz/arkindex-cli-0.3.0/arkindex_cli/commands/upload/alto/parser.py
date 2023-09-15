# -*- coding: utf-8 -*-
import logging
from math import floor
from typing import Optional

from lxml import etree as ET

logger = logging.getLogger(__name__)


def _is_alto_namespace(namespace: str) -> bool:
    return (
        namespace.startswith("http://www.loc.gov/standards/alto/")
        # Older URLs for ALTO≤2.0
        or namespace.startswith("http://schema.ccs-gmbh.com/docworks/")
    )


class AltoElement:
    def __init__(
        self,
        node: ET.Element,
        page_width: Optional[int] = None,
        page_height: Optional[int] = None,
        alto_namespace: Optional[str] = None,
        unit: str = "pixel",
        dpi_x: Optional[int] = None,
        dpi_y: Optional[int] = None,
    ):
        if alto_namespace:
            self.namespaces = {"alto": alto_namespace}
        else:
            alto_namespaces = set(filter(_is_alto_namespace, node.nsmap.values()))

            if len(alto_namespaces) == 1:
                self.namespaces = {"alto": alto_namespaces.pop()}
            elif len(alto_namespaces) > 1:
                raise ValueError(f"Multiple ALTO namespaces found: {alto_namespaces}")
            else:
                raise ValueError("ALTO namespace not found")

        assert not (
            (dpi_x is None) ^ (dpi_y is None)
        ), "The horizontal and vertical resolutions must be both set or both unset."
        assert (
            dpi_x is None or dpi_x > 0
        ), "The horizontal resolution must be a strictly positive integer."
        assert (
            dpi_y is None or dpi_y > 0
        ), "The vertical resolution must be a strictly positive integer."

        assert unit in ("pixel", "mm10"), f"Unsupported measurement unit {unit}"
        if unit == "mm10":
            assert (
                dpi_x is not None and dpi_y is not None
            ), "The horizontal and vertical resolutions must be set to import ALTO elements using the mm10 unit."

        self.node_name = ET.QName(node).localname.lower()
        self.strings = node.findall("{*}String", namespaces=self.namespaces)
        self.page_width = page_width or self.get_width(node)
        self.page_height = page_height or self.get_height(node)
        self.unit = unit
        self.dpi_x = dpi_x
        self.dpi_y = dpi_y
        # If there are more than one Page node in the file, the image id required
        # to build the IIIF url for the images is retrieved from the Page's
        # PHYSICAL_IMG_NR attribute and stored as page_image_id.
        self.page_image_id = self.get_page_image_id(node)
        self.content = node
        self.children = []

    def xml_int_value(self, node, attr_name):
        value = node.get(attr_name)
        if value is None:
            raise ValueError(f"Missing required value: {attr_name}")
        # The ALTO specification accepts float coordinates, but Arkindex only supports integers
        return round(float(value))

    def get_polygon_coordinates(self, node):
        if not (
            "HPOS" in node.attrib
            and "VPOS" in node.attrib
            and "WIDTH" in node.attrib
            and "HEIGHT" in node.attrib
        ):
            return

        # Skip elements with polygons with w or h <= 0 (invalid polygons)
        width = self.xml_int_value(node, "WIDTH")
        height = self.xml_int_value(node, "HEIGHT")
        if width <= 0 or height <= 0:
            return

        return {
            "x": self.xml_int_value(node, "HPOS"),
            "y": self.xml_int_value(node, "VPOS"),
            "width": width,
            "height": height,
        }

    def get_width(self, node):
        if "WIDTH" not in node.attrib:
            return
        return self.xml_int_value(node, "WIDTH")

    def get_height(self, node):
        if "HEIGHT" not in node.attrib:
            return
        return self.xml_int_value(node, "HEIGHT")

    def get_page_image_id(self, node):
        if "PHYSICAL_IMG_NR" not in node.attrib:
            return
        return node.get("PHYSICAL_IMG_NR")

    def ark_polygon(self, dict):
        """
        A polygon compatible with Arkindex.
        """
        if not dict:
            return None

        x, y, width, height = dict["x"], dict["y"], dict["width"], dict["height"]

        polygon = [
            [x, y],
            [x, y + height],
            [x + width, y + height],
            [x + width, y],
            [x, y],
        ]

        page_width, page_height = self.page_width, self.page_height

        # When using tenths of millimeters, we convert the coordinates to pixels
        if self.unit == "mm10":
            polygon = [
                [round(x * self.dpi_x / 254), round(y * self.dpi_y / 254)]
                for x, y in polygon
            ]
            # Also convert the page width and height, which also is in tenths of millimeters,
            # so we can trim the pixels properly and never go beyond the edges of the image
            page_width = floor(page_width * self.dpi_x / 254)
            page_height = floor(page_height * self.dpi_y / 254)

        # We trim the polygon of the element in the case where its dimensions are bigger than the dimensions of the image
        polygon = [
            [min(page_width, max(0, x)), min(page_height, max(0, y))]
            for x, y in polygon
        ]

        # We check there are always at least 4 different points
        if len(set(map(tuple, polygon))) < 4:
            return

        return polygon

    @property
    def has_children(self):
        return len(list(self.content)) > 0

    @property
    def polygon(self):

        coords = self.get_polygon_coordinates(self.content)

        # Special case for nodes when width and height are set, use full size
        if not coords and self.width and self.height:
            coords = {"x": 0, "y": 0, "width": self.width, "height": self.height}

        return self.ark_polygon(coords)

    @property
    def width(self):
        return self.get_width(self.content)

    @property
    def height(self):
        return self.get_height(self.content)

    @property
    def name(self):
        return self.content.get("LABEL", self.id)

    @property
    def id(self):
        return self.content.get("ID")

    def parse_children(self):
        if not self.has_children:
            return
        for child in self.content:
            child_element = AltoElement(
                child,
                page_width=self.page_width,
                page_height=self.page_height,
                alto_namespace=self.namespaces["alto"],
                unit=self.unit,
                dpi_x=self.dpi_x,
                dpi_y=self.dpi_y,
            )
            # String nodes are not sent to Arkindex as Elements, but their "CONTENT"
            # is sent as the transcription for their parent node.
            if child_element.node_name != "string":
                self.children.append(child_element)
                child_element.parse_children()

    @property
    def text(self):
        """
        Easy access to the node's transcription
        """
        if not len(self.strings):
            return

        return " ".join(string.attrib["CONTENT"] for string in self.strings).strip()


class RootAltoElement(AltoElement):
    def __init__(
        self,
        node: ET.Element,
        alto_namespace: Optional[str] = None,
        dpi_x: Optional[int] = None,
        dpi_y: Optional[int] = None,
    ):
        super().__init__(node, alto_namespace=alto_namespace, dpi_x=dpi_x, dpi_y=dpi_y)

        # Retrieve the file's measurement unit, used to specify the image(s) and polygons
        # dimensions. We support tenths of millimeters only when the DPI are set, and pixels whenever.
        try:
            self.unit = node.find(
                "{*}Description/{*}MeasurementUnit", namespaces=self.namespaces
            ).text
        except AttributeError:
            raise ValueError("The MesurementUnit is missing.")

        assert self.unit in (
            "pixel",
            "mm10",
        ), f"Unsupported measurement unit {self.unit}"
        if self.unit == "mm10":
            assert (
                self.dpi_x is not None and self.dpi_y is not None
            ), "The horizontal and vertical resolutions are required to parse ALTO files using the `mm10` measurement unit."

        try:
            # Retrieve the fileName node, which contains the identifier required to build the
            # IIIF url for the image (if there is only one Page node in the file.)
            self.filename = node.find(
                "{*}Description/{*}sourceImageInformation/{*}fileName",
                namespaces=self.namespaces,
            ).text
            assert self.filename, "Missing image file name"
        except AttributeError:
            raise ValueError("The fileName node is missing.")
