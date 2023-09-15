# -*- coding: utf-8 -*-

import json
import logging
from collections import namedtuple
from enum import Enum
from typing import Optional
from uuid import UUID

import requests

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BoundingBox = namedtuple("BoundingBox", ["x", "y", "width", "height"])


class Ordering(Enum):
    Position = "position"
    Name = "name"


def uuid_or_manual(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return UUID(value)
    except (TypeError, ValueError):
        if value != "manual":
            raise ValueError(
                "You must provide either a valid UUID or the string 'manual'."
            )
        return value


def parse_polygon(polygon):
    # getting polygon coordinates
    x_coords, y_coords = zip(*json.loads(polygon))

    # determining line box dimensions
    min_x, min_y = min(x_coords), min(y_coords)
    max_x, max_y = max(x_coords), max(y_coords)
    width, height = max_x - min_x, max_y - min_y
    return min_x, max_x, min_y, max_y, width, height


def bounding_box(polygon, offset_x=0, offset_y=0) -> Optional[BoundingBox]:
    """
    Gets the coordinates of the a polygon and sets the coordinates of the lower
    left point at which box starts, third value is the width of the box, the last
    one is the height,
    the y axis is switched in arkindex coordinates, starting from top left corner
    to the bottom whereas for reportlab the y axis starts from bottom left corner
    to the top,
    implies reportlab first point corresponds to arkindex (min_x,max_y)
    """

    min_x, _, _, max_y, width, height = parse_polygon(polygon)
    return BoundingBox(min_x - offset_x, max_y - offset_y, width, height)


def bounding_box_arkindex(polygon) -> Optional[BoundingBox]:
    """
    Get a bounding box with (min_x, min_y, width, height)
    """
    min_x, _, min_y, _, width, height = parse_polygon(polygon)
    return BoundingBox(min_x, min_y, width, height)


def image_download(image_url: str, image_name: str, temp_dir: str) -> str:
    """
    Gets an url and download the requested image on a temporary directory
    """

    image_path = temp_dir / f"{image_name}.jpg"
    # case where image_path already exists
    if image_path.is_file():
        return image_path

    flavoured_url = image_url + "/full/full/0/default.jpg"
    logger.info(f"downloading {flavoured_url}")
    r = requests.get(flavoured_url, stream=True)

    logger.info(f"saving image at {image_path}")
    with open(image_path, "wb") as f:
        for chunk in r.iter_content(4096):
            f.write(chunk)

    return image_path
