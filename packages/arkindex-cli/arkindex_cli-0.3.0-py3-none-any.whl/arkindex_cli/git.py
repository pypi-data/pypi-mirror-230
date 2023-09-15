# -*- coding: utf-8 -*-
import logging
import os
import re
import subprocess
from functools import cached_property
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GIT_SSH_REMOTE = re.compile(r"git@(?P<base>.+):(?P<project>.+)\.git")
CI_AUTHOR_REGEX = re.compile(r"^(?P<name>.+) <(?P<email>.+)>$")


class LocalGitRepository(object):
    """
    Helper class to retrieve the attributes of a git project locally
    by running commands via sub processes, or using GitLab CI variables.
    """

    def run(self, *args):
        return subprocess.check_output(args).decode().strip().splitlines()

    @property
    def in_ci(self):
        return os.environ.get("CI") == "true"

    @cached_property
    def url(self):
        if self.in_ci:
            return os.environ.get("CI_PROJECT_URL")

        remote = self.run("git", "remote", "get-url", "origin")
        assert (
            len(remote) == 1
        ), f"Current directory has multiple Git origin URL: {remote}"
        repository_url = remote[0]
        if not repository_url.startswith("http"):
            logger.debug(f"Trying to extract repository URL SSH remote {remote}")
            re_match = GIT_SSH_REMOTE.match(repository_url)
            if not re_match:
                raise ValueError(
                    f"Repository could not be detected from remote {remote}. "
                    "Please ensure you are in a Git project or manually set --repository-url."
                )
            attrs = re_match.groupdict()
            repository_url = urljoin(f"https://{attrs['base']}", attrs["project"])
        return repository_url

    @cached_property
    def hash(self):
        if self.in_ci:
            return os.environ.get("CI_COMMIT_SHA")

        logger.debug("Trying to extract revision hash from the current Git project")
        (revision_hash,) = self.run("git", "rev-parse", "HEAD")
        return revision_hash

    @cached_property
    def message(self):
        if self.in_ci:
            return os.environ.get("CI_COMMIT_MESSAGE")

        logger.debug("Trying to extract revision message from the current Git project")
        return "\n".join(
            self.run("git", "show", "--no-patch", "--format=%B", self.hash)
        )

    @cached_property
    def author(self):
        if self.in_ci:
            re_match = CI_AUTHOR_REGEX.fullmatch(os.environ.get("CI_COMMIT_AUTHOR", ""))
            if not re_match:
                raise ValueError(
                    "Unsupported commit author info found in CI_COMMIT_AUTHOR"
                )
            return re_match.group("name")

        logger.debug("Trying to extract revision author from the current Git project")
        (author,) = self.run(
            "git", "--no-pager", "show", "--no-patch", "--format=%an", self.hash
        )
        return author

    @cached_property
    def branch(self):
        if self.in_ci:
            return os.environ.get("CI_COMMIT_BRANCH")

        logger.debug("Trying to extract revision branch from the current Git project")
        (branch,) = self.run("git", "branch", "--show-current")
        return branch

    @cached_property
    def tags(self):
        if self.in_ci:
            tag = os.environ.get("CI_COMMIT_TAG")
            return [tag] if tag else []

        logger.debug(
            "Trying to extract a single revision tag from the current Git project"
        )
        return self.run("git", "--no-pager", "tag", "--points-at", self.hash)
