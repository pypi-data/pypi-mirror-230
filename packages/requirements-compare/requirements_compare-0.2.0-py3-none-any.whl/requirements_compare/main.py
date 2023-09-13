import argparse
import io
import pathlib
import subprocess
import sys
import typing

import packaging.requirements
import packaging.specifiers
import typer

app = typer.Typer(pretty_exceptions_enable=False)


class OldNewRequirements(typing.NamedTuple):
    old: packaging.requirements.Requirement
    new: packaging.requirements.Requirement


def clean_lines(f: io.TextIOWrapper) -> typing.Generator[str, None, None]:
    for line in f:
        # remove comments and hashes
        # because packaging.requirements.Requirement can't read hashes
        # and comments are useless here
        if not line.lstrip().startswith(("#", "--hash")):
            yield line.rstrip("\n").rstrip("\\")


def retrieve_equal_version(
    specifier: packaging.specifiers.SpecifierSet,
) -> packaging.specifiers.Specifier:
    """
    :raises ValueError: if no equal version is found
    """
    for s in specifier:
        if s.operator == "==":
            return s
    raise ValueError("No equal version found")


def retrieve_requirements(file: pathlib.Path) -> io.StringIO:
    p = subprocess.run(
        ["git", "show", f"HEAD:{file.name}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode != 0:
        typer.secho(p.stderr.decode(), fg=typer.colors.RED)
    content = io.StringIO(p.stdout.decode())
    return content


def compare_requirements(
    requirements: pathlib.Path,
) -> tuple[  # type: ignore
    set[packaging.requirements.Requirement],
    set[
        OldNewRequirements[
            packaging.requirements.Requirement, packaging.requirements.Requirement
        ]
    ],
    set[packaging.requirements.Requirement],
]:
    with requirements.open() as file:
        set_after = {
            packaging.requirements.Requirement(line) for line in clean_lines(file)
        }

    set_before = {
        packaging.requirements.Requirement(line)
        for line in clean_lines(retrieve_requirements(requirements))
    }

    new_requirements = {
        requirement.name: requirement
        for requirement in set_after.difference(set_before)
    }
    old_requirements = {
        requirement.name: requirement
        for requirement in set_before.difference(set_after)
    }

    added_requirements = {
        requirement
        for package_name, requirement in new_requirements.items()
        if package_name not in old_requirements
    }
    updated_requirements = {
        OldNewRequirements(old_requirements[package_name], requirement)
        for package_name, requirement in new_requirements.items()
        if package_name in old_requirements
    }
    removed_requirements = {
        requirement
        for package_name, requirement in old_requirements.items()
        if package_name not in new_requirements
    }

    return added_requirements, updated_requirements, removed_requirements


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "requirements_file",
        nargs="?",
        default=pathlib.Path("requirements.txt"),
        type=pathlib.Path,
    )
    parser.add_argument(
        "-o",
        nargs="?",
        default=pathlib.Path("description.md"),
        type=pathlib.Path,
        required=False,
    )
    return parser


def generate_changes(
    added_requirements: set[packaging.requirements.Requirement],
    updated: set[  # type: ignore
        OldNewRequirements[
            packaging.requirements.Requirement,
            packaging.requirements.Requirement,
        ]
    ],
    removed: set[packaging.requirements.Requirement],
) -> str:
    description = (
        [
            f"- Added `{requirement.name}` version "
            f"`{retrieve_equal_version(requirement.specifier).version}`"
            for requirement in added_requirements
        ]
        + [
            f"- Bump `{requirements.old.name}` from "
            f"`{retrieve_equal_version(requirements.old.specifier).version}` to "
            f"`{retrieve_equal_version(requirements.new.specifier).version}`"
            for requirements in updated
        ]
        + [
            f"- Removed `{requirement.name}` version "
            f"`{retrieve_equal_version(requirement.specifier).version}`"
            for requirement in removed
        ]
    )
    return "\r\n".join(description)


def main(requirements_file: pathlib.Path, output_file: pathlib.Path) -> None:
    added, updated, removed = compare_requirements(requirements_file)
    if output_file == pathlib.Path():
        return typer.echo(generate_changes(added, updated, removed), file=sys.stdout)

    with output_file.open("w") as file:
        typer.echo(generate_changes(added, updated, removed), file=file)


@app.command()
def rc(
    requirements_file: typing.Annotated[
        pathlib.Path, typer.Argument(help="The updated requirements file to compare")
    ],
) -> None:
    """
    Compare a local requirements file to its HEAD version and generate a description of
    the changes.
    """
    main(requirements_file, pathlib.Path())


if __name__ == "__main__":
    app()
