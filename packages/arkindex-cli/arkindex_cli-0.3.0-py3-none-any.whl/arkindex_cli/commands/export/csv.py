# -*- coding: utf-8 -*-

import csv
import fnmatch
import logging
from datetime import datetime, timezone
from itertools import chain
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from arkindex_cli.commands.export.utils import uuid_or_manual
from arkindex_export import (
    Classification,
    Element,
    ElementPath,
    Entity,
    EntityType,
    Image,
    Metadata,
    Transcription,
    TranscriptionEntity,
    open_database,
)
from arkindex_export.queries import list_children, list_parents
from peewee import JOIN, fn

logger = logging.getLogger(__name__)


def get_elements(parent_id=None, element_type=None, recursive=False):
    elements = Element.select()
    if parent_id:
        elements = elements.join(
            ElementPath, on=(Element.id == ElementPath.child_id)
        ).where(ElementPath.parent_id == parent_id)
        if recursive:
            elements = list_children(parent_id)
    if element_type:
        elements = elements.where(Element.type == element_type)
    return elements


def classes_columns(elements, classification_worker_version=None):
    classifications = Classification.select(Classification.class_name).distinct()
    # Filter by element id if the exported elements have been filtered by parent or type
    if elements is not None:
        classifications = classifications.where(
            Classification.element_id.in_(elements.select(Element.id))
        )
    if classification_worker_version:
        if classification_worker_version == "manual":
            classifications = classifications.where(
                Classification.worker_version_id.is_null()
            )
        else:
            classifications = classifications.where(
                Classification.worker_version_id == classification_worker_version
            )
    return [item.class_name for item in classifications]


def entity_type_columns(elements, entities_worker_version=None):
    entity_types = (
        EntityType.select(
            EntityType.name, Transcription.element_id, fn.COUNT("*").alias("count")
        )
        .join(Entity)
        .join(TranscriptionEntity)
        .join(Transcription)
        .group_by(Transcription.element_id, EntityType.name)
    )
    # Filter by element id if the exported elements have been filtered by parent or type
    if elements is not None:
        entity_types = entity_types.where(
            Transcription.element_id.in_(elements.select(Element.id))
        )
    if entities_worker_version:
        if entities_worker_version == "manual":
            entity_types = entity_types.where(
                TranscriptionEntity.worker_version_id.is_null()
            )
        else:
            entity_types = entity_types.where(
                TranscriptionEntity.worker_version_id == entities_worker_version
            )
    with_count = (
        EntityType.select(
            entity_types.c.name, fn.MAX(entity_types.c.count).alias("max_count")
        )
        .from_(entity_types)
        .group_by(entity_types.c.name)
    )

    # Name the columns
    columns = []
    for entity_type in with_count:
        if entity_type.max_count > 1:
            for i in range(1, entity_type.max_count + 1):
                column_name = f"entity_{entity_type.name}_{i}"
                assert (
                    column_name not in columns
                ), f"Duplicate entity type column: {column_name}."
                columns.append(column_name)
                i += 1
        else:
            if entity_type.name not in columns:
                columns.append(f"entity_{entity_type.name}")

    return columns


def metadata_columns(elements, load_parents=False, recursive=False):
    """
    When using the with_parent_metadata option, for each element we need to retrieve its own
    metadata as well as the metadata of every one of its parents: we need to recursively list
    all the parents of every relevant element.
    To do so, we build a recursive subquery that returns two columns:
    - exported_element_id (the elements which correspond to a line in the output CSV)
    - metadata_element_id (the parent elements whose metadata are added to the element's own).
    When the with_parent_metadata option isn't used, the two columns contain the same elements.
    This recursive subquery is then joined with the Metadata table, adding all of an element's
    parents' metadata to its own metadata, to be output on its line in the CSV.
    """
    # Use all elements when there are no parent or type filters
    if elements is None:
        elements = Element.select()

    # Removing the ordering by elements as it cannot come before the UNION clause.
    base = (
        elements.order_by()
        .select(Element.id, Element.id)
        .cte(
            "element_parents",
            recursive=load_parents,
            columns=("exported_element_id", "metadata_element_id"),
        )
    )
    if load_parents:
        parents = ElementPath.select(
            base.c.exported_element_id, ElementPath.parent_id
        ).join(base, on=(base.c.metadata_element_id == ElementPath.child_id))
        cte = base.union(parents)
    # If not loading the parents' metadata, the CTE doesn't become recursive and the metadata
    # elements are the same as the exported elements.
    else:
        cte = base

    metadata = (
        Metadata.select(
            Metadata.name, cte.c.exported_element_id, fn.COUNT("*").alias("count")
        )
        .join(cte, on=(Metadata.element_id == cte.c.metadata_element_id))
        .group_by(Metadata.name, cte.c.exported_element_id)
    )

    # If elements listing is recursive, using list_children from arkindex_export, then `elements`
    # already has a CTE and defining a new one overwrites it (see
    # https://docs.peewee-orm.com/en/latest/peewee/api.html#Query.with_cte). However, we can use
    # the hidden `_cte_list` attribute to retrieve it
    # (https://github.com/coleifer/peewee/blob/a6f479dc0e8063a9a7f7053b04d93f34d67737ce/peewee.py#L2111)
    if elements._cte_list:
        metadata = metadata.with_cte(*elements._cte_list, cte)
    else:
        metadata = metadata.with_cte(cte)

    with_count = (
        Metadata.select(metadata.c.name, fn.MAX(metadata.c.count).alias("max_count"))
        .from_(metadata)
        .group_by(metadata.c.name)
    )

    # Name the columns
    columns = []
    for md in with_count:
        if md.max_count > 1:
            for i in range(1, md.max_count + 1):
                column_name = f"{md.name}_{i}"
                assert (
                    column_name not in columns
                ), f"Duplicate metadata column: {column_name}."
                columns.append(column_name)
                i += 1
        else:
            if md.name not in columns:
                columns.append(md.name)

    return columns


def element_classes(element_id, classification_worker_version=None):
    element_classifications = Classification.select(
        Classification.class_name, Classification.confidence
    ).where(Classification.element_id == element_id)
    if classification_worker_version:
        if classification_worker_version == "manual":
            element_classifications = element_classifications.where(
                Classification.worker_version_id.is_null()
            )
        else:
            element_classifications = element_classifications.where(
                Classification.worker_version_id == classification_worker_version
            )
    return element_classifications


def element_entities(element_id, entities_worker_version=None):
    entities = (
        EntityType.select(
            EntityType.name.alias("type_name"),
            Entity.name.alias("name"),
            fn.ROW_NUMBER().over(partition_by=([EntityType.name])).alias("number"),
        )
        .join(Entity)
        .join(TranscriptionEntity)
        .join(Transcription)
        .where(Transcription.element_id == element_id)
        .group_by(Entity.id)
        .order_by(EntityType.name, Entity.name)
    )
    if entities_worker_version:
        if entities_worker_version == "manual":
            entities = entities.where(TranscriptionEntity.worker_version_id.is_null())
        else:
            entities = entities.where(
                TranscriptionEntity.worker_version_id == entities_worker_version
            )

    return entities.namedtuples()


def element_metadata(element_id, load_parents=False):
    metadata = Metadata.select(Metadata.name, Metadata.value).where(
        Metadata.element_id == element_id
    )
    if load_parents:
        metadata = Metadata.select(Metadata.name, Metadata.value).where(
            Metadata.element.in_(list_parents(element_id))
        )
    return Metadata.select(
        metadata.c.name,
        metadata.c.value,
        fn.ROW_NUMBER().over(partition_by=([metadata.c.name])).alias("number"),
    ).from_(metadata)


def element_dict(
    item,
    with_classes=False,
    with_metadata=False,
    with_parent_metadata=False,
    with_entities=False,
    classes_columns=None,
    metadata_columns=None,
    entity_type_columns=None,
    classification_worker_version=None,
    entities_worker_version=None,
):
    assert (
        not with_metadata or metadata_columns is not None
    ), "Metadata columns are required to output element metadata"
    assert (
        not with_classes or classes_columns is not None
    ), "Classes columns are required to output element classifications"
    assert (
        not with_entities or entity_type_columns is not None
    ), "Entity type columns are required to output element entities"
    serialized_element = {
        "id": item.id,
        "name": item.name,
        "type": item.type,
        "image_id": None,
        "image_url": None,
        "polygon": item.polygon,
        "worker_version_id": item.worker_version_id,
        "created": datetime.fromtimestamp(item.created, tz=timezone.utc).isoformat(),
    }
    if item.image_id:
        serialized_element["image_id"] = item.image_id
        serialized_element["image_url"] = item.image.url
    if with_metadata and metadata_columns:
        serialized_element = {
            **serialized_element,
            **{key: None for key in metadata_columns},
        }
        element_md = element_metadata(item.id, load_parents=with_parent_metadata)
        for metadata in element_md:
            # If metadata.name is in metadata_columns, it means that there is only ever
            # one metadata with this name in all the listed elements, no multiple values.
            if metadata.name in serialized_element:
                # Check that there isn't already a value for that metadata on that element
                assert serialized_element[metadata.name] is None
                serialized_element[metadata.name] = metadata.value
            # If metadata.name is not in metadata_columns, iterate through the list of
            # values and assign them to {metadata.name}_1, {metadata.name}_2 etc.
            else:
                # Check that there isn't already a value for that metadata on that element
                assert serialized_element[f"{metadata.name}_{metadata.number}"] is None
                serialized_element[
                    f"{metadata.name}_{metadata.number}"
                ] = metadata.value
    if with_classes and classes_columns:
        classes = element_classes(item.id, classification_worker_version)
        if classes.count():
            for class_name in classes_columns:
                serialized_element[class_name] = next(
                    (
                        item.confidence
                        for item in classes
                        if item.class_name == class_name
                    ),
                    None,
                )
    if with_entities and entity_type_columns:
        serialized_element = {
            **serialized_element,
            **{key: None for key in entity_type_columns},
        }
        entities = element_entities(item.id, entities_worker_version)
        for entity in entities:
            if f"entity_{entity.type_name}" in serialized_element:
                serialized_element[f"entity_{entity.type_name}"] = entity.name
            # If entity.type_name is not in serialized_element, iterate through
            # the list of entity.name and assign them to entity_{entity.type_name}_1,
            # entity_{entity.type_name}_2 etc.
            else:
                serialized_element[
                    f"entity_{entity.type_name}_{entity.number}"
                ] = entity.name

    return serialized_element


def run(
    database_path: Path,
    output_path: Path,
    profile_slug: Optional[str] = None,
    parent: Optional[UUID] = None,
    type: Optional[str] = None,
    recursive: Optional[bool] = False,
    with_classes: Optional[bool] = False,
    with_metadata: Optional[bool] = False,
    with_parent_metadata: Optional[bool] = False,
    with_entities: Optional[bool] = False,
    classification_worker_version: Optional[str] = None,
    entities_worker_version: Optional[str] = None,
    output_header: Optional[List[str]] = [],
):
    database_path = database_path.absolute()
    assert database_path.is_file(), f"Database at {database_path} not found"
    if with_parent_metadata:
        assert (
            with_metadata
        ), "The --with-parent-metadata option can only be used if --with-metadata is set."
    if entities_worker_version:
        assert (
            with_entities
        ), "The --entities-worker-version option can only be used if --with-entities is set."

    output_path = output_path.absolute()

    if recursive:
        assert (
            parent
        ), "The recursive option can only be used if a parent_element is given. If no parent_element is specified, element listing is recursive by default."

    open_database(database_path)

    elements = get_elements(parent, type, recursive)

    csv_header = [
        "id",
        "name",
        "type",
        "image_id",
        "image_url",
        "polygon",
        "worker_version_id",
        "created",
    ]
    cl_columns = None
    if with_classes:
        if not parent and not type:
            cl_columns = classes_columns(None)
        else:
            cl_columns = classes_columns(elements)
        csv_header = csv_header + cl_columns
    md_columns = None
    if with_metadata:
        # Fetch all the metadata keys to build one CSV column by key
        if not parent and not type:
            md_columns = metadata_columns(
                None, load_parents=with_parent_metadata, recursive=recursive
            )
        else:
            md_columns = metadata_columns(
                elements, load_parents=with_parent_metadata, recursive=recursive
            )
        csv_header = csv_header + md_columns
    et_columns = None
    if with_entities:
        if not parent and not type:
            et_columns = entity_type_columns(
                None,
                entities_worker_version,
            )
        else:
            et_columns = entity_type_columns(
                elements,
                entities_worker_version,
            )
        csv_header = csv_header + et_columns

    if output_header:
        filtered_header = list(
            chain(*[fnmatch.filter(csv_header, header) for header in output_header])
        )
        # Keep the initial order of the CSV columns
        csv_header = [header for header in csv_header if header in filtered_header]

    elements = elements.select(Element, Image).join(
        Image, JOIN.LEFT_OUTER, on=[Image.id == Element.image_id]
    )

    with open(output_path, "w", encoding="UTF8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=csv_header)
        writer.writeheader()
        for element in elements:
            serialized_element = {
                key: value
                for key, value in element_dict(
                    element,
                    with_classes,
                    with_metadata,
                    with_parent_metadata,
                    with_entities,
                    classes_columns=cl_columns,
                    metadata_columns=md_columns,
                    entity_type_columns=et_columns,
                    classification_worker_version=classification_worker_version,
                    entities_worker_version=entities_worker_version,
                ).items()
                if key in csv_header
            }
            writer.writerow(serialized_element)
    logger.info(f"Exported elements successfully written to {output_path}.")


def add_csv_parser(subcommands):
    csv_parser = subcommands.add_parser(
        "csv",
        description="Read data from an exported database and generate a CSV file.",
        help="Generates a CSV file from an Arkindex export.",
    )
    csv_parser.add_argument(
        "--parent",
        type=UUID,
        help="Limit the export to the children of a given element.",
    )
    csv_parser.add_argument(
        "--type", type=str, help="Limit the export to elements of a given type."
    )
    csv_parser.add_argument(
        "--recursive", action="store_true", help="Get elements recursively."
    )
    csv_parser.add_argument(
        "--with-classes", action="store_true", help="Retrieve element classes."
    )
    csv_parser.add_argument(
        "--classification-worker-version",
        type=uuid_or_manual,
        help="The worker version that created the classifications that will be in the csv",
    )
    csv_parser.add_argument(
        "--with-metadata", action="store_true", help="Retrieve element metadata."
    )
    csv_parser.add_argument(
        "--with-parent-metadata",
        action="store_true",
        help="Recursively retrieve metadata of element ancestors.",
    )
    csv_parser.add_argument(
        "--with-entities", action="store_true", help="Retrieve element entities."
    )
    csv_parser.add_argument(
        "--entities-worker-version",
        type=uuid_or_manual,
        help="Only retrieve the entities created by a specific worker version.",
    )
    csv_parser.add_argument(
        "-o",
        "--output",
        default=Path.cwd() / "elements.csv",
        type=Path,
        help="Path to a CSV file where results will be outputted. Defaults to '<current_directory>/elements.csv'.",
        dest="output_path",
    )
    csv_parser.add_argument(
        "-f",
        "--field",
        nargs="+",
        type=str,
        help="Limit the CSV columns to the selected fields",
        dest="output_header",
    )
    csv_parser.set_defaults(func=run)
