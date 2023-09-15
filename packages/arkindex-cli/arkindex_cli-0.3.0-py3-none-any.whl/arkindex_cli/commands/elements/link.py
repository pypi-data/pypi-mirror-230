# -*- coding: utf-8 -*-
from typing import Optional
from uuid import UUID

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.elements.utils import get_children_list, get_parent_element


def add_linking_parser(subcommands):
    link_parser = subcommands.add_parser(
        "link",
        description="Link one or a list of elements to a parent element.",
        help="",
    )
    parent_input = link_parser.add_mutually_exclusive_group(required=True)
    parent_input.add_argument(
        "--parent",
        help="UUID of the existing parent element.",
        type=UUID,
    )
    parent_input.add_argument(
        "--create", help="Create a new parent element.", action="store_true"
    )
    child_input = link_parser.add_mutually_exclusive_group(required=True)
    child_input.add_argument(
        "--child",
        help="One or more element UUID(s).",
        nargs="+",
        type=UUID,
    )
    child_input.add_argument(
        "--uuid-list", help="Path to a list of UUIDs, one per line."
    )
    child_input.add_argument(
        "--selection",
        help="Use the elements in the selection on Arkindex.",
        action="store_true",
    )
    child_input.add_argument(
        "--stray-pages",
        help="All the page elements (from the specified parent element's corpus) that do not have a folder parent element.",
        action="store_true",
    )
    link_parser.set_defaults(func=run)


def run(
    parent: Optional[UUID] = None,
    create: Optional[UUID] = False,
    child: Optional[UUID] = None,
    uuid_list: Optional[str] = None,
    selection: Optional[bool] = False,
    stray_pages: Optional[bool] = False,
    profile_slug: Optional[str] = None,
):
    profiles = Profiles()
    client = profiles.get_api_client_or_exit(profile_slug)

    # retrieving or creating the parent element and its corpus to check that
    # parent and child(ren) elements belong to the same corpus
    parent_element = get_parent_element(parent, create, client)
    children = get_children_list(
        client,
        child=child,
        uuid_list=uuid_list,
        selection=selection,
        stray_pages=stray_pages,
        parent_element=parent_element,
    )
    for child_uuid in children:
        child_element = client.request("RetrieveElement", id=child_uuid)
        assert (
            parent_element["corpus"]["id"] == child_element["corpus"]["id"]
        ), "Parent and child element do not belong to the same corpus and cannot be linked."
        client.request(
            "CreateElementParent", child=child_uuid, parent=parent_element["id"]
        )
        print(
            "Elements {} and {} successfully linked.".format(
                child_uuid, parent_element["id"]
            )
        )
