# -*- coding: utf-8 -*-
from typing import Optional
from uuid import UUID

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.elements.utils import get_children_list


def add_unlinking_parser(subcommands):
    unlink_parser = subcommands.add_parser(
        "unlink",
        description="Unlink one or a list of elements from a parent element.",
        help="",
    )
    unlink_parser.add_argument(
        "--parent",
        help="UUID of the parent element.",
        type=UUID,
    )
    child_input = unlink_parser.add_mutually_exclusive_group(required=True)
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
        help="Use the elements in the selected on Arkindex.",
        action="store_true",
    )
    unlink_parser.add_argument(
        "--orphan",
        help="Unlink an element from the specified parent even if it is its only parent.",
        action="store_true",
    )
    unlink_parser.set_defaults(func=run)


def run(
    parent: UUID,
    child: Optional[UUID] = None,
    uuid_list: Optional[str] = None,
    selection: Optional[bool] = False,
    orphan: Optional[bool] = False,
    profile_slug: Optional[str] = None,
):
    profiles = Profiles()
    client = profiles.get_api_client_or_exit(profile_slug)
    children = get_children_list(
        client, child=child, uuid_list=uuid_list, selection=selection
    )
    for child_uuid in children:
        if not orphan:
            existing_parents = client.request(
                "ListElementParents", id=child_uuid, folder=True, recursive=True
            )["count"]
            if existing_parents < 2:
                print(
                    "Element {} does not have another parent folder element and cannot be unlinked from {}.".format(
                        child_uuid, parent
                    )
                )
            else:
                client.request("DestroyElementParent", child=child_uuid, parent=parent)
                print(
                    "Elements {} and {} successfully unlinked.".format(
                        parent, child_uuid
                    )
                )
        else:
            client.request("DestroyElementParent", child=child_uuid, parent=parent)
            print(
                "Elements {} and {} successfully unlinked.".format(parent, child_uuid)
            )
