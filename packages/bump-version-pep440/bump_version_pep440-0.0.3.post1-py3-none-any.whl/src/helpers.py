import toml
import typer
from packaging.version import InvalidVersion, Version


def get_current_version(version_str: str = None) -> Version:
    if version_str:
        try:
            version = Version(version_str)
            # Additional validation to ensure the version string is exactly what the user provided
            if str(version) != version_str:
                raise InvalidVersion
            return version
        except InvalidVersion:
            error_message = typer.style(
                f"Invalid version string: {version_str}. Please provide a valid PEP 440 compliant version string.",
                fg=typer.colors.RED,
            )
            typer.echo(error_message)
            raise typer.Exit(code=1)

    try:
        data = toml.load("pyproject.toml")
    except FileNotFoundError:
        error_message = typer.style(
            "Error: pyproject.toml file not found in the current directory.",
            fg=typer.colors.RED,
        )
        typer.echo(error_message)
        raise typer.Exit(code=1)

    version_str = data.get("tool", {}).get("poetry", {}).get("version")
    if not version_str:
        error_message = typer.style(
            "Error: Version not specified in pyproject.toml under [tool.poetry].",
            fg=typer.colors.RED,
        )
        typer.echo(error_message)
        raise typer.Exit(code=1)

    return Version(version_str)


def bump_major(version: Version) -> Version:
    return Version(f"{version.major + 1}.0.0")


def bump_minor(version: Version) -> Version:
    return Version(f"{version.major}.{version.minor + 1}.0")


def bump_micro(version: Version) -> Version:
    return Version(f"{version.major}.{version.minor}.{version.micro + 1}")


def bump_pre(version: Version, pre_type: str) -> Version:
    pre_num = 1
    if version.pre:
        pre_letter, pre_existing_num = version.pre
        if pre_letter == pre_type:
            pre_num = pre_existing_num + 1
    return Version(f"{version.base_version}{pre_type}{pre_num}")


def bump_post(version: Version) -> Version:
    post_num = version.post if version.post else 0
    return Version(f"{version.base_version}.post{post_num + 1}")


def bump_dev(version: Version) -> Version:
    dev_num = version.dev if version.dev else 0
    return Version(f"{version.base_version}.dev{dev_num + 1}")
