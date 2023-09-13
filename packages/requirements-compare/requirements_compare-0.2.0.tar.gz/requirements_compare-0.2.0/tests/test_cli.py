import typer.testing

from requirements_compare import app

runner = typer.testing.CliRunner()


def test_app_2(requirements_file):
    requirements_file.write_text(
        "example_package==2.0.0\nlast_package==1.0.0",
    )

    result = runner.invoke(app, [requirements_file.name])
    assert result.exit_code == 0
    assert "added `last_package` version `1.0.0`" in result.stdout.lower()
    assert "bump `example_package` from `1.0.0` to `2.0.0`" in result.stdout.lower()
