# -*- coding: utf-8 -*-
import logging
from uuid import UUID

from apistar.exceptions import ErrorResponse

from arkindex_cli.utils import ask

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s/%(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def get_elements_from_ids(client, uuids: list, element_type):
    elements = []
    for element_id in uuids:
        try:
            element_info = client.request("RetrieveElement", id=element_id)
            elements.append(element_info)
        except ErrorResponse as e:
            if e.status_code == 404:
                raise Exception(
                    f"Element {element_id} couldn't be found; check your UUIDs."
                ) from None
            else:
                logger.error(
                    f"Couldn't retrieve element {element_id}: {e.status_code} — {e.content}."
                )
    assert len(elements) > 0, "No elements could be retrieved from the given UUIDs."
    filtered_elements = elements
    if element_type:
        filtered_elements = [
            element for element in elements if element["type"] == element_type
        ]
    if len(elements) > len(filtered_elements):
        logger.warning(
            f"Ignored {len(elements)-len(filtered_elements)} element(s) that is/are not of type {element_type}."
        )
    return filtered_elements


def retrieve_elements(client, **kwargs):
    """
    Retrieve target elements from:
    - one or more UUID(s) passed in the command
    - a file (one UUID) per line
    - the selection on Arkindex
    with or without an element type restriction
    """

    element_ids = kwargs.get("elements")
    uuids_file = kwargs.get("uuid_list")
    use_selection = kwargs.get("selection")
    element_type = kwargs.get("element_type")

    if use_selection:
        elements = client.paginate("ListSelection")
        filtered_elements = elements
        if element_type:
            filtered_elements = [
                element for element in elements if element["type"] == element_type
            ]
        assert (
            len(filtered_elements) > 0
        ), "The selection on Arkindex is empty or only contains elements that are not of the specified element type."
    elif uuids_file:
        element_ids = [line.strip() for line in open(uuids_file, "r").readlines()]
        assert (
            len(element_ids) > 0
        ), "The list of element UUIDs could not be recovered. Check your input file."
        filtered_elements = get_elements_from_ids(client, element_ids, element_type)
    elif element_ids:
        filtered_elements = get_elements_from_ids(client, element_ids, element_type)
    else:
        raise ValueError(
            "One of (elements, uuid-list, selection) must be set as input."
        )
    return filtered_elements


def get_children_list(client, **kwargs):
    """
    Get a list of element UUID from:
    - one single UUID passed in the command
    - a file (one UUID per line)
    - the selection on Arkindex
    - the pages in a corpus that do not have a parent folder element
    """

    uuid_list = kwargs.get("uuid_list", None)
    child = kwargs.get("child", None)
    selection = kwargs.get("selection", False)
    stray_pages = kwargs.get("stray_pages", False)
    parent_element = kwargs.get("parent_element", None)

    if uuid_list is not None:
        children = [line.strip() for line in open(uuid_list, "r").readlines()]
        assert (
            len(children) > 0
        ), "The list of element UUIDs could not be recovered. Check your input file."
    elif child is not None:
        children = child
        assert len(children) > 0, "No child element UUID was given."
    elif selection:
        children = [item["id"] for item in client.paginate("ListSelection")]
        assert len(children) > 0, "The selection on Arkindex is empty."
    elif stray_pages:
        children = []
        corpus_id = parent_element["corpus"]["id"]
        all_pages = client.paginate("ListElements", corpus=corpus_id, type="page")
        for one_page in all_pages:
            page_parents = client.request(
                "ListElementParents", id=one_page["id"], folder=True
            )
            if page_parents["count"] == 0:
                children.append(one_page["id"])
        assert len(children) > 0, f"There are no stray pages in corpus {corpus_id}."
    else:
        raise ValueError(
            "A single UUID, file, Arkindex selection or 'stray-pages' is required as child(ren) input."
        )
    return children


def get_parent_element(parent, create, client):
    """
    - Retrieve an existing element information from its UUID
    - Create a new element and return its information
    """
    if parent is not None:
        parent_element = client.request("RetrieveElement", id=parent)
    elif create:
        parent_corpus = UUID(
            ask("Enter the UUID of the corpus in which to create the element").strip()
        )
        parent_type = ask("Enter the element type of the element to create").strip()

        # checking that the specified type exists in the specified corpus
        if not any(
            item["slug"] == parent_type
            for item in client.request("RetrieveCorpus", id=parent_corpus)["types"]
        ):
            raise ValueError(
                f"Element type {parent_type} does not exist in corpus {parent_corpus}."
            )
        parent_name = ask("Enter the name of the element to create").strip()
        body = {"type": parent_type, "corpus": str(parent_corpus), "name": parent_name}
        parent_element = client.request("CreateElement", body=body)
    else:
        raise ValueError("An element UUID or 'create' is required as parent input.")
    return parent_element


def retrieve_children(
    client,
    corpus=None,
    parent=None,
    type=None,
    recursive=False,
    with_classes=False,
    with_metadata=False,
):
    extra_filters = {}
    if type:
        extra_filters["type"] = type
    if with_classes:
        extra_filters["with_classes"] = True
    if with_metadata:
        extra_filters["with_metadata"] = True

    if corpus is not None:
        # ListElements is recursive by default
        # if we don't want it to be, we must set top_level to True
        if not recursive:
            extra_filters["top_level"] = True

        children = client.paginate("ListElements", corpus=corpus, **extra_filters)

        extra_str = ("" if recursive else " top-level") + (f" {type}" if type else "")
        assert (
            len(children) > 0
        ), f"There are no{extra_str} elements in corpus {corpus}."
    elif parent is not None:
        extra_filters["recursive"] = recursive

        children = client.paginate("ListElementChildren", id=parent, **extra_filters)

        extra_str = ("" if recursive else " direct") + (f" {type}" if type else "")
        assert (
            len(children) > 0
        ), f"There are no{extra_str} children in parent {parent}."
    else:
        raise ValueError(
            "Either a corpus UUID or a parent UUID is required to retrieve children."
        )

    return children
