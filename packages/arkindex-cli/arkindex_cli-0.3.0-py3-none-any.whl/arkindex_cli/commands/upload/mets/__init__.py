# -*- coding: utf-8 -*-
import errno
import logging
import urllib.parse
from pathlib import Path
from typing import Optional
from uuid import UUID

from apistar.exceptions import ErrorResponse
from rich.progress import Progress

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.upload.alto import get_element_type
from arkindex_cli.commands.upload.mets.cache import Cache
from arkindex_cli.commands.upload.mets.parser import (
    MetsProcessingError,
    RootMetsElement,
)

logger = logging.getLogger(__name__)


def trailing_slash_url(value):
    """Check an URL ends with a /"""
    assert isinstance(value, str)
    parts = urllib.parse.urlparse(value)
    assert parts.scheme in ("http", "https")
    if parts.path:
        assert parts.path.endswith("/"), "Must end with a /"
    return value


def trailing_slash_str(value):
    """Check an optional string ends with a /"""
    if value:
        assert isinstance(value, str)
        assert value.endswith("/"), "Must end with a /"
    return value


def add_mets_parser(subcommands):

    mets = subcommands.add_parser(
        "mets",
        description="Upload METS XML documents to Arkindex.",
        help="Upload METS XML documents to Arkindex.",
    )
    mets.add_argument(
        "path",
        help="Path to a METS file.",
        type=Path,
    )
    mets.add_argument(
        "corpus_id",
        help="ID of the Arkindex corpus.",
        type=UUID,
    )
    mets.add_argument(
        "--element-id",
        help="ID of the Arkindex element.",
        type=UUID,
        required=True,
    )
    mets.add_argument(
        "--iiif-base-url",
        help="Base URL of the IIIF server where the images used by the METS file are exposed",
        type=trailing_slash_url,
        default="https://europe-gamma.iiif.teklia.com/iiif/2/",
    )
    mets.add_argument(
        "--iiif-prefix",
        help="Prefix on the IIIF server behind which the images used by the METS file are exposed",
        type=trailing_slash_str,
    )
    mets.add_argument(
        "--dpi-x",
        help="Horizontal resolution of the image, in dots per inch, to be used for ALTO files using coordinates in tenths of millimeters.\n"
        "Strictly positive integer. Ignored for files using coordinates in pixels.",
        type=int,
    )
    mets.add_argument(
        "--dpi-y",
        help="Vertical resolution of the image, in dots per inch, to be used for ALTO files using coordinates in tenths of millimeters.\n"
        "Strictly positive integer. Ignored for files using coordinates in pixels.",
        type=int,
    )
    mets.add_argument(
        "--skip-metadatas",
        help="Skipping Alto ID metadata publication speeds up a lot the execution time",
        action="store_true",
    )
    mets.add_argument(
        "--worker-run-id",
        help="Worker Run used to publish elements and transcriptions in bulk. This is required to use bulk endpoints and speed up publication.",
        type=UUID,
    )
    mets.set_defaults(func=run)


def run(
    path: Path,
    corpus_id: UUID,
    element_id: UUID,
    iiif_base_url: str,
    iiif_prefix: Optional[str] = None,
    dpi_x: Optional[int] = None,
    dpi_y: Optional[int] = None,
    worker_run_id: Optional[UUID] = None,
    skip_metadatas: bool = False,
    profile_slug: Optional[str] = None,
):
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        client = Profiles().get_api_client_or_exit(profile_slug)

    # Parse TOC
    assert path.exists(), f"Cannot find METS at {path}"
    root = RootMetsElement(path, iiif_base_url, iiif_prefix, dpi_x, dpi_y)

    if not worker_run_id:
        logger.info(
            "Upload METS in slow mode (Set --worker-run-id to use bulk endpoints)"
        )

    # Check the existence of the top element
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Fetching parent element")
        try:
            client.request("RetrieveElement", id=element_id)
        except ErrorResponse as e:
            logger.error(
                f"Could not retrieve parent element {element_id}: HTTP {e.status_code} - {e.content}"
            )
            return errno.EREMOTEIO

    # Check that every type used by the tree is available on the corpus
    for type_slug in root.list_required_types():
        get_element_type(
            client, corpus_id, type_slug, types_dict=None, create_types=True
        )

    # Setup cache next to mets file
    Cache(path.parent / f"{path.stem}_cache.json")

    # Publish all elements recursively starting from root
    try:
        root.publish(
            arkindex_client=client,
            parent_id=element_id,
            corpus_id=corpus_id,
            publish_metadatas=not skip_metadatas,
            worker_run_id=worker_run_id,
        )
    except MetsProcessingError:
        logger.error(f"Failed to publish METS file @ {path}")
    except KeyboardInterrupt:
        pass

    # Make sure to save cache on keyboard interrupt
    del Cache._instance
