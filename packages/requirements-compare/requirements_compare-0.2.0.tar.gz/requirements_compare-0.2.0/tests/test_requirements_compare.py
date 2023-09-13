"""Sample test module."""
import io

import pytest

from requirements_compare.main import main


def test_removed(requirements_file, output_file):
    """Test main function."""
    requirements_file.write_text("")
    main(
        requirements_file,
        output_file,
    )

    result = output_file.read_text().lower()
    assert "removed" in result
    assert "example_package" in result
    assert "`1.0.0`" in result


def test_added(requirements_file, output_file):
    """Test main function."""
    requirements_file.write_text("example_package==1.0.0\nanother_package==1.0.0")
    main(
        requirements_file,
        output_file,
    )

    result = output_file.read_text().lower()
    assert "added" in result
    assert "another_package" in result
    assert "`1.0.0`" in result

    assert "example_package" not in result


def test_bump(requirements_file, output_file):
    """Test main function."""
    requirements_file.write_text(
        "example_package==2.0.0",
    )
    main(
        requirements_file,
        output_file,
    )

    result = output_file.read_text().lower()
    assert "bump" in result
    assert "example_package" in result
    assert "`1.0.0` to `2.0.0`" in result


@pytest.fixture
def retrieve_requirements_2(monkeypatch):
    def mock_retrieve_requirements(requirements_file):
        return io.StringIO("example_package==1.0.0\nanother_package==1.0.0")

    monkeypatch.setattr(
        "requirements_compare.main.retrieve_requirements",
        mock_retrieve_requirements,
    )


def test_all(requirements_file, output_file, retrieve_requirements_2):
    """Test main function."""
    requirements_file.write_text("example_package==2.0.0\nlast_package==1.0.0\n")
    main(
        requirements_file,
        output_file,
    )

    result = output_file.read_text().lower()
    assert "bump" in result
    assert "example_package" in result
    assert "`1.0.0` to `2.0.0`" in result

    assert "removed" in result
    assert "another_package" in result
    assert "`1.0.0`" in result

    assert "bump" in result
    assert "last_package" in result
    assert "`1.0.0`" in result
