# -*- coding: utf-8 -*-
import logging
import os
from typing import Optional

from arkindex import ArkindexClient
from rich.progress import Progress

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.models.utils import (
    create_archive,
    create_model_version,
    create_or_retrieve_model,
    find_model_path,
    parse_yml_config,
    upload_to_s3,
    validate_model_version,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def add_publish_parser(subcommands) -> None:
    publish_parser = subcommands.add_parser(
        "publish",
        description="Publish every ML models of this git repository.",
        help="Publish ML models to Arkindex.",
    )
    publish_parser.set_defaults(func=run)


def publish_model(
    client: ArkindexClient,
    name: str,
    configuration: dict,
) -> None:
    """This takes a model associated to a worker and publishes a new version of the model"""
    logger.info(f"Publishing {name}")

    # Find the model file associated
    model_path = configuration.pop("model")
    path_to_model = find_model_path(
        config_model_path=model_path,
    )

    assert path_to_model, f"The model could not be loaded using {model_path}"

    # Try to create a model
    # On 201, use the given id
    # On 400, use the given id key='name'
    # On 403 abort and log error
    model_id = create_or_retrieve_model(client=client, name=name)

    # Create a version for this model
    model_version = create_model_version(
        client=client,
        model_id=model_id,
        tag=os.environ.get("CI_COMMIT_TAG"),
        description=name,
        configuration=configuration,
    )

    # Create the zst archive, get its hash and size
    with create_archive(path=path_to_model) as (
        path_to_archive,
        hash,
        size,
        archive_hash,
    ):
        upload_to_s3(archive_path=path_to_archive, model_version_details=model_version)

        # Validate the model version with hash, archive_hash and size
        valid_version = validate_model_version(
            client=client,
            model_version_id=model_version["id"],
            size=size,
            hash=hash,
            archive_hash=archive_hash,
        )

    if valid_version["id"] != model_version["id"]:
        logger.warning(
            f"Model version {model_version['id']} has been marked as erroneous and left aside. "
            f"Using existing model version {valid_version['id']}"
        )


def run(
    profile_slug: Optional[str] = None,
) -> None:
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        client = Profiles().get_api_client_or_exit(profile_slug)

    # Parse .arkindex.yml => retrieve worker name, path and configuration
    workers = parse_yml_config(worker_config_path=".arkindex.yml")

    # For each worker, do_publish
    for worker_name, worker_configuration in workers.items():
        try:
            publish_model(
                client,
                worker_name,
                worker_configuration,
            )
        except Exception as e:
            msg = getattr(e, "content", repr(e))
            logger.exception(f"{worker_name} publishing has failed with error: {msg}")
            logger.error("Skipping this model.")

    logger.info("All done.")
