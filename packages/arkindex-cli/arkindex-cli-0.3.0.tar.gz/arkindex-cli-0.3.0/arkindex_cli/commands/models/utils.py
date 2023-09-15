# -*- coding: utf-8 -*-
import hashlib
import logging
import os
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import NewType, Optional, Tuple, Union
from uuid import UUID

import apistar
import requests
import yaml
import zstandard as zstd
from apistar.exceptions import ErrorResponse
from arkindex import ArkindexClient

logger = logging.getLogger(__name__)
CHUNK_SIZE = 1024


FilePath = NewType("FilePath", Path)
Hash = NewType("Hash", str)
FileSize = NewType("FileSize", int)
Archive = Tuple[FilePath, Hash, FileSize]

# Teklia's convention
DEFAULT_MODEL_DIR = Path("/usr/share/teklia")


def build_clean_payload(**kwargs):
    """
    Remove null attributes from an API body payload
    """
    return {key: value for key, value in kwargs.items() if value is not None}


def find_model_path(config_model_path: str) -> Path:
    """We try the following paths in that order and return the first that exists
    - /usr/share/teklia/${config_model_path}
    - ${config_model_path}
    - ./models/${config_model_path}
    """

    # Get relative path to model
    relative_path = config_model_path
    # If it follows Teklia's convention, we remove the prefix
    if relative_path.startswith(str(DEFAULT_MODEL_DIR)):
        relative_path = Path(relative_path).relative_to(DEFAULT_MODEL_DIR)

    # Tested paths
    possible_paths = [
        DEFAULT_MODEL_DIR / relative_path,
        Path(".") / relative_path,
        Path("models") / relative_path,
    ]
    for path_to_model in possible_paths:
        if path_to_model.exists():
            logger.info(f"Found model in {path_to_model}.")
            return path_to_model


@contextmanager
def create_archive(
    path: FilePath,
) -> Archive:
    """
    Create tar archive with everything that's in the folder at path
    Keep the hierarchy but parent folder should not be included
    Save the absolute path of each file added to compute their hash later
    """

    assert path.is_dir(), "This path must resolve to a directory"

    content_hasher = hashlib.md5()

    # Remove extension from the model filename
    _, path_to_tar_archive = tempfile.mkstemp(prefix="teklia-", suffix=".tar")

    with tarfile.open(path_to_tar_archive, "w") as tar:
        tar.add(name=path, arcname=".")

        # Walk and find each file in the dir
        for member in tar.getnames():
            filepath = path / member
            if filepath.is_dir():
                # We don't care about directories
                continue

            # Compute hash
            with filepath.open("rb") as file_data:
                for chunk in iter(lambda: file_data.read(CHUNK_SIZE), b""):
                    content_hasher.update(chunk)

    # Compress the archive
    _, path_to_zst_archive = tempfile.mkstemp(prefix="teklia-", suffix=".tar.zst")

    compressor = zstd.ZstdCompressor(level=3)
    archive_hasher = hashlib.md5()
    with open(path_to_zst_archive, "wb") as archive_file, open(
        path_to_tar_archive, "rb"
    ) as model_data:
        for model_chunk in iter(lambda: model_data.read(CHUNK_SIZE), b""):
            compressed_chunk = compressor.compress(model_chunk)
            archive_hasher.update(compressed_chunk)
            archive_file.write(compressed_chunk)

    # Remove the tar archive
    os.remove(path_to_tar_archive)

    # Get content hash, archive size and hash
    hash = content_hasher.hexdigest()
    size = os.path.getsize(path_to_zst_archive)
    archive_hash = archive_hasher.hexdigest()

    yield path_to_zst_archive, hash, size, archive_hash

    # Remove the zstd archive
    os.remove(path_to_zst_archive)


def create_or_retrieve_model(client: ArkindexClient, name: str):
    """Create a new model or retrieve the id of the existing one (with the same name)"""
    status = 200
    try:
        r = client.request("CreateModel", body={"name": name})
        # New model was created
        return r["id"]
    except apistar.exceptions.ErrorResponse as e:
        r = e.content
        status = e.status_code
        if status == 400:
            # Model already exists but user has access to it. The model id was returned in payload
            return r["id"]
        elif status == 403:
            # Model exists but user has no access to it, raise
            raise Exception(f"Permission denied to publish {name}")
        else:
            raise


def parse_worker_configuration(worker):
    """
    Read the worker configuration from both the basic and the user configuration defined.
    In the latter case, only default values are included.
    """
    # Read basic config
    configuration = worker.get("configuration", {})

    # Read user_config defaults if there are any
    if "user_configuration" in worker:
        # Add default values (if set) to user_configuration
        configuration.update(
            {
                key: value["default"]
                for key, value in worker["user_configuration"].items()
                if "default" in value
            }
        )
    return configuration


def parse_yml_config(worker_config_path: str, single_worker: bool = False) -> dict:
    """Parse .arkindex.yml and retrieve each workers data"""
    with open(worker_config_path, "r") as config_file:
        try:
            data = yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            logger.error(exc)
            return None

    if single_worker:
        return {data["name"]: parse_worker_configuration(data)}

    # Parse each worker separately
    workers = data.get("workers", [])
    if len(workers) > 0 and isinstance(workers[0], str):
        parsed_worker_configurations = dict()
        for worker_path in workers:
            parsed_worker_configurations.update(
                parse_yml_config(worker_config_path=worker_path, single_worker=True)
            )
        return parsed_worker_configurations
    else:
        return {
            worker["name"]: parse_worker_configuration(worker) for worker in workers
        }


def create_model_version(
    client: ArkindexClient,
    model_id: str,
    tag: Optional[str] = None,
    description: Optional[str] = None,
    configuration: Optional[dict] = {},
    parent: Optional[Union[str, UUID]] = None,
) -> dict:
    # Create a new model version with optional base attributes
    return client.request(
        "CreateModelVersion",
        id=model_id,
        body=build_clean_payload(
            tag=tag,
            description=description,
            configuration=configuration,
            parent=parent,
        ),
    )


def upload_to_s3(archive_path: str, model_version_details: dict) -> None:
    s3_put_url = model_version_details.get("s3_put_url")
    logger.info("Uploading to s3...")
    # Upload the archive on s3
    with open(archive_path, "rb") as archive:
        r = requests.put(
            url=s3_put_url,
            data=archive,
            headers={"Content-Type": "application/zstd"},
        )
    r.raise_for_status()


def validate_model_version(
    client: ArkindexClient,
    model_version_id: Union[str, UUID],
    hash: str,
    size: int,
    archive_hash: str,
) -> dict:
    # Sets the model version as `Available`, once its archive has been uploaded to S3.
    logger.info("Validating the model version...")
    try:
        return client.request(
            "ValidateModelVersion",
            id=model_version_id,
            body={"size": size, "hash": hash, "archive_hash": archive_hash},
        )
    except ErrorResponse as e:
        msg = getattr(e, "content", repr(e))
        if e.status_code == 409:
            logger.warning(f"An available model version exists with hash {hash}")
            # Do not keep empty model versions, it won't be used anyways
            destroy_model_version(client=client, model_version_id=model_version_id)
            return e.content
        logger.error(f"Failed to update model version: {msg}")
        raise e


def destroy_model_version(
    client: ArkindexClient,
    model_version_id: Union[str, UUID],
) -> None:
    logger.info("Deleting the model version...")
    try:
        client.request(
            "DestroyModelVersion",
            id=model_version_id,
        )
    except ErrorResponse as e:
        msg = getattr(e, "content", repr(e))
        logger.error(f"Failed to delete model version: {msg}")
        raise e
