from __future__ import annotations

import os

import pytest
from bmi_dbseabed.cli import main
from click.testing import CliRunner


@pytest.fixture
def cli_runner():
    return CliRunner()


def test_command_line_interface(cli_runner):
    result = cli_runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output

    result = cli_runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_output(cli_runner, tmpdir):
    result = cli_runner.invoke(
        main,
        [
            "--var_name=carbonate",
            "--bbox=-66.8,18,-66.2,18.4",
            "error",
        ],
    )
    assert result.exit_code != 0


def test_var_name(cli_runner):
    result = cli_runner.invoke(
        main,
        [
            "--var_name=error",
            "--bbox=-66.8,18,-66.2,18.4",
            "test.tif",
        ],
    )
    assert result.exit_code != 0


def test_bbox(cli_runner):
    result = cli_runner.invoke(
        main,
        [
            "--var_name=carbonate",
            "--bbox=error",
            "test.tif",
        ],
    )
    assert result.exit_code != 0


@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_data_download(cli_runner, tmpdir):
    with tmpdir.as_cwd():
        result = cli_runner.invoke(
            main,
            [
                "--var_name=carbonate",
                "--bbox=-98,18,-80,31",
                "test.tif",
            ],
        )

        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 1
