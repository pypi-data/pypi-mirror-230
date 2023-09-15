# -*- coding: utf-8 -*-
import csv
import logging
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Optional
from uuid import UUID

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.elements.utils import retrieve_children

logger = logging.getLogger(__name__)

CSV_HEADER_DEFAULT = [
    "id",
    "name",
    "type",
    "image_id",
    "image_url",
    "polygon",
    "worker_version_id",
    "created",
]
CSV_HEADER_CLASSES = CSV_HEADER_DEFAULT + [
    "class_name",
    "class_id",
    "classification_confidence",
]


class ElementsList:
    """
    List elements from a given corpus or parent element.
    """

    def __init__(
        self,
        api_client,
        corpus: Optional[UUID] = None,
        parent: Optional[UUID] = None,
        type: Optional[str] = None,
        recursive: Optional[bool] = False,
        with_classes: Optional[bool] = False,
        with_metadata: Optional[bool] = False,
        output_path: Optional[Path] = None,
    ):
        self.client = api_client
        self.corpus = corpus
        self.parent = parent
        self.type = type
        self.recursive = recursive
        self.with_classes = with_classes
        self.with_metadata = with_metadata

        if output_path is None:
            output_path = Path.cwd() / "elements.csv"
        self.output_path = output_path

        # Since one metadata can be set multiple times, with different values, on one element,
        # we need to know the maximum count for each metadata across all listed elements in
        # order to be able to build column names for metadata like {metadata}_1, {metadata}_2 ...
        self.metadata = {}
        self.metadata_names_max_counts = {}

    def serialize_child(self, child):
        """
        Takes an element as input, and outputs one or more dictionaries to be used
        by writerow, depending on the with_classes parameter and whether an element
        has classes or not (if an element has n classes, yields n dictionaries)
        """

        classes = child.get("classes")
        metadata = child.get("metadata")
        base_dict = {
            "id": child["id"],
            "name": child["name"],
            "type": child["type"],
            "image_id": None,
            "image_url": None,
            "polygon": None,
            "worker_version_id": child["worker_version_id"],
            "created": child["created"],
        }
        if child.get("zone"):
            base_dict["image_id"] = child["zone"]["image"]["id"]
            base_dict["image_url"] = child["zone"]["image"]["url"]
            base_dict["polygon"] = child["zone"]["polygon"]

        if self.with_metadata:
            self.metadata[child["id"]] = defaultdict(list)
            for item in metadata:
                self.metadata[child["id"]][item["name"]].append(item["value"])
            # Get the values count for each metadata; if the metadata already has a values count
            # in self.metadata_names_max_counts and the new count is bigger, update it; else save
            # that count.
            for metadata_name, values in self.metadata[child["id"]].items():
                self.metadata_names_max_counts[metadata_name] = max(
                    len(values), self.metadata_names_max_counts.get(metadata_name, 0)
                )

        if self.with_classes:
            if classes:
                for one_class in classes:
                    yield {
                        **base_dict,
                        **{
                            "class_name": one_class["ml_class"]["name"],
                            "class_id": one_class["id"],
                            "classification_confidence": one_class["confidence"],
                        },
                    }
            else:
                yield {
                    **base_dict,
                    **{
                        "class_name": None,
                        "class_id": None,
                        "classification_confidence": None,
                    },
                }
        else:
            yield base_dict

    def metadata_columns(self):
        columns = []
        for md_name, md_count in self.metadata_names_max_counts.items():
            if md_count == 1:
                assert md_name not in columns, f"Duplicate metadata column: {md_name}."
                columns.append(md_name)
            else:
                for i in range(1, md_count + 1):
                    numbered_name = f"{md_name}_{i}"
                    assert (
                        numbered_name not in columns
                    ), f"Duplicate metadata column: {numbered_name}."
                    columns.append(numbered_name)
                    i += 1
        return columns

    def write_to_csv(self, elements, tmp_file):
        csv_header = CSV_HEADER_CLASSES if self.with_classes else CSV_HEADER_DEFAULT

        with open(tmp_file.name, "w", encoding="UTF8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=csv_header)
            writer.writeheader()

            for item in elements:
                for item in self.serialize_child(item):
                    writer.writerow(item)

    def run(self):
        children = retrieve_children(
            self.client,
            corpus=self.corpus,
            parent=self.parent,
            type=self.type,
            recursive=self.recursive,
            with_classes=self.with_classes,
            with_metadata=self.with_metadata,
        )

        with tempfile.NamedTemporaryFile() as tmp_file:
            self.write_to_csv(children, tmp_file)

            if self.with_metadata:
                with open(tmp_file.name, "r") as input:
                    reader = csv.DictReader(input)
                    csv_header = reader.fieldnames
                    with open(
                        self.output_path, "w", encoding="UTF8", newline=""
                    ) as output:
                        metadata_columns = self.metadata_columns()
                        csv_header = csv_header + metadata_columns
                        writer = csv.DictWriter(output, fieldnames=csv_header)
                        writer.writeheader()
                        for row in reader:
                            element_metadata = self.metadata[row["id"]]
                            for name, values in element_metadata.items():
                                if name in metadata_columns:
                                    assert len(values) == 1
                                    row[name] = values[0]
                                else:
                                    for i, value in enumerate(values, start=1):
                                        row[f"{name}_{i}"] = value
                            writer.writerow(row)
            else:
                shutil.copy2(tmp_file.name, self.output_path)
            logger.info(f"Listed elements successfully written to {self.output_path}.")


def add_list_parser(subcommands):
    list_parser = subcommands.add_parser(
        "list",
        description="List all elements in a corpus or under a specified parent and output results in a CSV file.",
        help="",
    )
    root = list_parser.add_mutually_exclusive_group(required=True)
    root.add_argument(
        "--corpus",
        help="UUID of an existing corpus.",
        type=UUID,
    )
    root.add_argument(
        "--parent",
        help="UUID of an existing parent element.",
        type=UUID,
    )
    list_parser.add_argument(
        "--type",
        help="Limit the listing using this slug of an element type.",
        type=str,
    )
    list_parser.add_argument(
        "--recursive",
        help="List elements recursively.",
        action="store_true",
    )
    list_parser.add_argument(
        "--with-classes",
        help="List elements with their classifications.",
        action="store_true",
    )
    list_parser.add_argument(
        "--with-metadata",
        help="List elements with their metadata.",
        action="store_true",
    )
    list_parser.add_argument(
        "--output",
        default=Path.cwd() / "elements.csv",
        type=Path,
        help="Path to a CSV file where results will be outputted. Defaults to '<current_directory>/elements.csv'.",
        dest="output_path",
    )
    list_parser.set_defaults(func=run)


def run(profile_slug: Optional[str] = None, **kwargs):
    profiles = Profiles()
    api_client = profiles.get_api_client_or_exit(profile_slug)
    ElementsList(api_client, **kwargs).run()
