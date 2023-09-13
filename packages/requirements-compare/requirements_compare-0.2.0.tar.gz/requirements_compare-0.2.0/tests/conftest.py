import io
import pathlib

import pytest


@pytest.fixture(autouse=True)
def retrieve_requirements(monkeypatch):
    def mock_retrieve_requirements(requirements_file):
        return io.StringIO("example_package==1.0.0")

    monkeypatch.setattr(
        "requirements_compare.main.retrieve_requirements",
        mock_retrieve_requirements,
    )


@pytest.fixture
def requirements_file() -> pathlib.Path:
    requirements_file_ = pathlib.Path("requirements.txt")
    yield requirements_file_
    requirements_file_.unlink()


@pytest.fixture
def output_file() -> pathlib.Path:
    output_file_ = pathlib.Path("output.txt")
    yield output_file_
    output_file_.unlink()
