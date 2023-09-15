# -*- coding: utf-8 -*-
import logging
import random
from textwrap import dedent
from typing import Optional
from urllib.parse import urljoin
from uuid import UUID

from apistar.exceptions import ErrorResponse
from rich.progress import track

from arkindex_cli.auth import Profiles

logger = logging.getLogger(__name__)


class Splits:
    """
    Split the elements of one or more given element type(s) inside a project or parent
    element between train, validation and test folders for machine learning processes.
    """

    def __init__(
        self,
        profile_slug: Optional[str] = None,
        project: Optional[UUID] = None,
        folder: Optional[UUID] = None,
        element_type: Optional[list] = ["page"],
        dataset_name: Optional[str] = "Training dataset",
        train_ratio: Optional[float] = 0.8,
        validation_ratio: Optional[float] = 0.1,
        test_ratio: Optional[float] = 0.1,
        nb_elements: Optional[int] = None,
        recursive: Optional[bool] = False,
        folder_type: Optional[str] = "folder",
    ):
        self.project_id = project
        self.folder_id = folder
        self.types = element_type
        self.dataset_name = dataset_name
        self.train_ratio = train_ratio
        self.val_ratio = validation_ratio
        self.test_ratio = test_ratio
        self.nb_elems = nb_elements
        self.children_recursive = recursive
        self.folder_type = folder_type

        profiles = Profiles()
        # The profile URL is used later on
        profile = profiles.get_or_exit(profile_slug)
        self.instance_url = profile.url
        self.api_client = profiles.get_api_client(profile)

    def check_arguments(self):
        # --project and --folder are mutually exclusive
        assert (self.project_id is None) ^ (
            self.folder_id is None
        ), "Only one of --project or --folder may be set."

        # The --recursive option only makes sense if using a folder element
        if self.children_recursive:
            assert (
                self.folder_id
            ), "The --recursive option can only be used with the --folder one."

        # Check the ratios
        assert (
            0 < self.train_ratio < 1
        ), "The training ratio must be strictly between 0 and 1 (not included)."
        assert (
            0 < self.test_ratio < 1
        ), "The test ratio must be strictly between 0 and 1 (not included)."
        assert (
            self.val_ratio < 1
        ), "The validation ratio must be strictly inferior to 1."

        # Check that the sum of all the ratios is 1
        assert (
            self.train_ratio + self.val_ratio + self.test_ratio == 1
        ), "The sum of the train, validation and test ratios must be equal to 1."

        # Check that the given parent folder exists
        if self.folder_id:
            logger.info("Retrieving parent element…")
            try:
                folder = self.api_client.request("RetrieveElement", id=self.folder_id)
            except ErrorResponse as e:
                if e.status_code == 404:
                    raise ValueError(
                        f"Parent element {self.folder_id} does not exist. Check the UUID."
                    ) from None
                else:
                    raise

        self.project_id = self.project_id or folder["corpus"]["id"]

        # Check that the given parent project exists
        logger.info("Retrieving project information…")
        try:
            corpus = self.api_client.request("RetrieveCorpus", id=self.project_id)
        except ErrorResponse as e:
            if e.status_code == 404:
                raise ValueError(
                    f"Project {self.project_id} does not exist. Check the UUID."
                ) from None
            else:
                raise

        # Check that the parent folder is a folder
        folder_types = [
            item["slug"]
            for item in corpus["types"]
            if "folder" in item and item["folder"]
        ]
        if self.folder_id and folder["type"] not in folder_types:
            logger.warning(f"Parent element {folder['name']} is not a folder type.")

        # Check that the type of the folders to create exists in the project, and is of folder type
        assert (
            self.folder_type in folder_types
        ), f"There is no folder type {self.folder_type!r} in project {corpus['name']}."

        # Check that the given element types exist in the project
        type_slugs = [item["slug"] for item in corpus["types"]]
        missing = [item for item in self.types if item not in type_slugs]
        assert (
            len(missing) == 0
        ), f"Element type(s) {', '.join(missing)} not found in project {corpus['name']}."

    def make_splits(self, elements):
        # Shuffle the list of IDs
        random.shuffle(elements)
        # Use nb_elems if set
        if self.nb_elems:
            if self.nb_elems > len(elements):
                logger.warning(
                    dedent(
                        f"The number of elements to use was set to {self.nb_elems}, but only "
                        f"{len(elements)} were returned. Using all the returned elements."
                    )
                )
            else:
                elements = elements[: self.nb_elems]
        # Build the sets
        train_count = int(self.train_ratio * len(elements))
        if self.val_ratio:
            val_count = int(self.val_ratio * len(elements))
        train_set = elements[:train_count]
        valtest = elements[train_count:]
        assert not any(
            item in train_set for item in valtest
        ), "Some items are present both in the training and validation/test sets."
        val_set = []
        if self.val_ratio:
            val_set = valtest[:val_count]
            test_set = valtest[val_count:]
            assert not any(
                item in test_set for item in val_set
            ), "Some items are present both in the validation and test sets."
        else:
            test_set = valtest
        return train_set, val_set, test_set

    def create_folders(self):
        try:
            dataset_folder = self.api_client.request(
                "CreateElement",
                body={
                    "corpus": str(self.project_id),
                    "name": self.dataset_name,
                    "type": self.folder_type,
                },
            )
            train_folder = self.api_client.request(
                "CreateElement",
                body={
                    "parent": dataset_folder["id"],
                    "corpus": str(self.project_id),
                    "name": "Train",
                    "type": self.folder_type,
                },
            )
            test_folder = self.api_client.request(
                "CreateElement",
                body={
                    "parent": dataset_folder["id"],
                    "corpus": str(self.project_id),
                    "name": "Test",
                    "type": self.folder_type,
                },
            )
            val_folder = None
            if self.val_ratio:
                val_folder = self.api_client.request(
                    "CreateElement",
                    body={
                        "parent": dataset_folder["id"],
                        "corpus": str(self.project_id),
                        "name": "Validation",
                        "type": self.folder_type,
                    },
                )
        except ErrorResponse as e:
            raise ValueError(
                f"Failed creating folders: {e.status_code} -- {e.content}"
            ) from e
        return dataset_folder, train_folder, val_folder, test_folder

    def link(self, elements, folder):
        for item in track(
            elements,
            transient=True,
            description=f"Linking {len(elements)} elements to folder {folder['name']}",
        ):
            try:
                self.api_client.request(
                    "CreateElementParent", child=item, parent=folder["id"]
                )
            except ErrorResponse as e:
                logger.error(
                    f"Failed linking element {item} to parent {folder['id']}: {e.status_code} -- {e.content}"
                )

    def run(self):
        self.check_arguments()
        elements = []
        for element_type in self.types:
            logger.info(f"Retrieving {element_type} elements…")
            try:
                if self.folder_id:
                    response = self.api_client.paginate(
                        "ListElementChildren",
                        id=self.folder_id,
                        type=element_type,
                        recursive=self.children_recursive,
                    )
                elif self.project_id:
                    response = self.api_client.paginate(
                        "ListElements", corpus=self.project_id, type=element_type
                    )
                elements += [item["id"] for item in response]
            except ErrorResponse:
                raise
        assert len(elements), "No elements were returned."

        training, validation, testing = self.make_splits(elements)
        dataset, train_folder, val_folder, test_folder = self.create_folders()
        self.link(training, train_folder)
        self.link(testing, test_folder)
        if self.val_ratio:
            self.link(validation, val_folder)
        dataset_url = urljoin(self.instance_url, f"element/{dataset['id']}")
        logger.info(
            f"Training dataset successfully created! You can access it here: {dataset_url}."
        )


def add_splits_parser(subcommands):
    splits_parser = subcommands.add_parser(
        "ml-splits",
        description="Split elements between train, val and test folders.",
        help="""
            Create a dataset for machine learning training and testing.
            Split elements of one or more given element types, belonging to a project
            or a given parent element, between train, val and test folders according
            to a given ratio.
        """,
    )
    source = splits_parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--project",
        help="UUID of a project to get the elements from.",
        type=UUID,
    )
    source.add_argument(
        "--folder",
        help="UUID of a parent element to get the elements from.",
        type=UUID,
    )
    splits_parser.add_argument(
        "--element-type",
        help="One or more element types to retrieve. Defaults to 'page'.",
        type=str,
        nargs="+",
        default=["page"],
    )
    splits_parser.add_argument(
        "--recursive",
        help="Recursively list children elements (if using a folder element).",
        action="store_true",
    )
    splits_parser.add_argument(
        "--train-ratio",
        help="""
            The proportion of the retrieved elements to put in the training data folder.
            A number between 0 and 1.
            0 (no training data) and 1 (only training data) are not valid values.
            Defaults to 0.8.
        """,
        default=0.8,
        type=float,
    )
    splits_parser.add_argument(
        "--validation-ratio",
        help="""
            The proportion of the retrieved elements to put in the validation data folder.
            A number between 0 and 1.
            Defaults to 0.1.
            1 (only validation data) is not a valid value. 0 (no validation data) is allowed.
        """,
        default=0.1,
        type=float,
    )
    splits_parser.add_argument(
        "--test-ratio",
        help="""
            The proportion of the retrieved elements to put in the test data folder.
            A number between 0 and 1.
            0 (no testing data) and 1 (only testing data) are not valid values.
            Defaults to 0.1.
        """,
        default=0.1,
        type=float,
    )
    splits_parser.add_argument(
        "--dataset-name",
        help="""
            The name of the dataset folder which will be created at the root of the project,
            which will containing the train, validation and test folders.
            Defaults to "Training dataset".
        """,
        type=str,
        default="Training dataset",
    )
    splits_parser.add_argument(
        "--nb-elements",
        help="""
            Limit the number of retrieved elements. If not set, all elements corresponding
            to the given element type and parent UUID will be retrieved.
        """,
        type=int,
    )
    splits_parser.add_argument(
        "--folder-type",
        help="""
            The element type of the folders (dataset, train, val and test) to be created.
            Defaults to 'folder'.
        """,
        type=str,
        default="folder",
    )
    splits_parser.set_defaults(func=run)


def run(profile_slug: Optional[str] = None, **kwargs):
    Splits(profile_slug, **kwargs).run()
