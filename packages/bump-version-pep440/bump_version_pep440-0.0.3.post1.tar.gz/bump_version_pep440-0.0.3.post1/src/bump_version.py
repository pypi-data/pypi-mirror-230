# src/bump_version.py
import logging
import subprocess
from typing import Optional, Union

import toml
from packaging.version import Version

from .helpers import (
    bump_dev,
    bump_major,
    bump_micro,
    bump_minor,
    bump_post,
    bump_pre,
    get_current_version,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def bump_version(
    version_type: str,
    current_version: Union[str, Version] = None,
    new_version: Union[str, Version] = None,
    commit: bool = False,
    commit_message: Optional[str] = None,
    dry_run: bool = False,
    tag: bool = False,
    tag_name: Optional[str] = None,
) -> str:
    """
    Bump the version based on the provided version type and other parameters.

    Args:
    - version_type (str): The type of version bump ("major", "minor", "micro", "a", "b", "rc", "post", "dev").
    - current_version (Optional[str]): If provided, this version will be used instead of reading from pyproject.toml.
    - new_version (Optional[str]): If provided, this version will be set instead of incrementing the current version.
    - commit (bool): If True, a git commit will be created. (default: False)
    - commit_message (Optional[str]): Custom commit message. If not provided, default will be used: "Bump version: {current_version} → {new_version}"
    - dry_run (bool): If True, no actual changes will be made, only printed.
    - tag (bool): If True, a git tag will be created.
    - tag_name (Optional[str]): Custom tag name. If not provided, the new version will be used.

    Returns:
    - str: The new version.
    """

    # Load the default configuration from pyproject.toml
    try:
        config = toml.load("pyproject.toml")["tool"]["bump-version"]
    except (FileNotFoundError, KeyError):
        config = {}

    # Use provided arguments or fall back to defaults from pyproject.toml
    current_version = current_version or config.get(
        "current_version", get_current_version()
    )
    new_version = new_version or config.get("new_version")
    commit = commit or config.get("commit", False)
    commit_message = commit_message or config.get(
        "commit_message", "Bump version: {current_version} → {new_version}"
    )
    tag = tag or config.get("tag", False)
    tag_name = tag_name or config.get("tag_name", "{new_version}")
    dry_run = dry_run or config.get("dry_run", False)

    # Convert current_version to a Version instance if it's a string
    if isinstance(current_version, str):
        current_version = Version(current_version)

    # Convert new_version to a Version instance if it's a string
    if isinstance(new_version, str):
        new_version = Version(new_version)

    # Actual bumping logic based on version_type
    if not new_version:
        if version_type == "major":
            new_version = bump_major(current_version)
        elif version_type == "minor":
            new_version = bump_minor(current_version)
        elif version_type == "micro":
            new_version = bump_micro(current_version)
        elif version_type in ["a", "b", "rc"]:
            new_version = bump_pre(current_version, version_type)
        elif version_type == "post":
            new_version = bump_post(current_version)
        elif version_type == "dev":
            new_version = bump_dev(current_version)
        else:
            logger.error(
                f"Invalid version type provided: {version_type}"
            )  # Logging the error
            raise ValueError(f"Invalid version type: {version_type}")

    # Check if the new version is greater than the current version
    if new_version <= current_version:
        logger.error(
            f"New version {new_version} is not greater than the current version {current_version}."
        )
        raise ValueError(
            f"New version {new_version} must be greater than the current version {current_version}."
        )

    # Dry run
    if not dry_run:
        data = toml.load("pyproject.toml")
        data["tool"]["poetry"]["version"] = str(new_version)
        with open("pyproject.toml", "w") as f:
            toml.dump(data, f)

    # Git commit
    if commit and not dry_run:
        commit_msg = commit_message.format(
            current_version=current_version, new_version=new_version
        )
        try:
            subprocess.run(["git", "add", "pyproject.toml"], check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        except subprocess.CalledProcessError:
            print(
                "Failed to create a git commit. Make sure you're in a git repository and have git installed."
            )

    # Git tag
    if tag and not dry_run:
        tag_name_formatted = tag_name.format(new_version=new_version)
        try:
            subprocess.run(["git", "tag", tag_name_formatted], check=True)
        except subprocess.CalledProcessError:
            print(
                "Failed to create a git tag. Make sure you're in a git repository and have git installed."
            )

    return str(new_version)
