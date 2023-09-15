# -*- coding: utf-8 -*-
import argparse
import csv
import logging
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from rich.console import Console
from rich.progress import track

from arkindex_export import (
    Entity,
    EntityType,
    Transcription,
    TranscriptionEntity,
    open_database,
)
from peewee import Value

logger = logging.getLogger(__name__)


def retrieve_transcription_entities(instance_url):
    return (
        TranscriptionEntity.select(
            TranscriptionEntity.transcription_id.alias("transcription_id"),
            Transcription.element_id.alias("element_id"),
            (
                Value(f"{instance_url.rstrip('/')}/element/").concat(
                    Transcription.element_id
                )
            ).alias("element_url"),
            TranscriptionEntity.entity_id.alias("entity_id"),
            EntityType.name.alias("entity_type"),
            Entity.name.alias("entity_value"),
            Entity.metas.alias("entity_metas"),
            TranscriptionEntity.length,
            TranscriptionEntity.offset,
        )
        .join(Entity)
        .join(EntityType)
        .switch(TranscriptionEntity)
        .join(Transcription)
        .order_by(TranscriptionEntity.transcription_id, TranscriptionEntity.entity_id)
        .dicts()
    )


def run(
    database_path: Path,
    output_path: Path,
    instance_url: str,
    profile_slug: Optional[str] = None,
):
    database_path = database_path.absolute()
    assert database_path.is_file(), f"Database at {database_path} not found"

    parsed_url = urlparse(instance_url)
    assert parsed_url.scheme and parsed_url.netloc, f"{instance_url} is not a valid url"

    csv_header = [
        "transcription_id",
        "element_id",
        "element_url",
        "entity_id",
        "entity_value",
        "entity_type",
        "entity_metas",
        "offset",
        "length",
    ]

    open_database(database_path)
    tr_entities = retrieve_transcription_entities(instance_url)

    writer = csv.DictWriter(output_path, fieldnames=csv_header)
    writer.writeheader()
    for tr_entity in track(
        tr_entities.iterator(),
        description="Exporting transcription entities",
        total=TranscriptionEntity.select().count(),
        console=Console(file=sys.stderr),
    ):
        writer.writerow(tr_entity)

    logger.info(
        f"Exported transcription entities successfully written to {output_path.name}."
    )


def add_entities_parser(subcommands) -> None:
    parser = subcommands.add_parser(
        "entities",
        help="Export entities from a given Arkindex project.",
        description="Export a project's transcription entities.",
    )
    parser.add_argument(
        "--output",
        help="Path to the CSV file which will be created",
        default=sys.stdout,
        type=argparse.FileType("w", encoding="UTF-8"),
        dest="output_path",
    )
    parser.add_argument(
        "--instance-url",
        help="URL of the Arkindex instance of the exported project.",
        type=str,
        required=True,
    )
    parser.set_defaults(func=run)
