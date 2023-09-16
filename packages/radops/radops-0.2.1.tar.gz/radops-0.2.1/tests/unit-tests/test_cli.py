import os
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from typer.testing import CliRunner

from radops.cli import app

runner = CliRunner()


@pytest.fixture
def mock_list_files():
    with patch(
        "radops.cli.data_lake.list_files_and_folders"
    ) as mock_list_files_and_folders:
        with patch(
            "radops.cli.data_lake.list_local_files"
        ) as mock_list_local_files:
            yield mock_list_local_files, mock_list_files_and_folders


@pytest.fixture
def mock_file_exists_in_cloud():
    with patch(
        "radops.cli.data_lake.File.exists_in_cloud"
    ) as mock_exists_in_cloud:
        yield mock_exists_in_cloud


@pytest.fixture
def mock_download():
    with patch(
        "radops.cli.data_lake.File.exists_locally"
    ) as mock_exists_locally:
        with patch(
            "radops.cli.data_lake.File.download_from_cloud"
        ) as mock_download_from_cloud:
            # mock_exists_locally.return_value = False/
            # mock_download_from_cloud.return_value = Mock()
            yield mock_exists_locally, mock_download_from_cloud


def test_ls(mock_list_files):
    # Set up mock responses
    mock_list_files[0].return_value = ["file1"]
    mock_list_files[1].return_value = [["file1", "file2"], []]

    result = runner.invoke(app, ["datalake", "ls"])
    assert result.exit_code == 0

    assert "file1" in result.stdout
    assert "file2" in result.stdout


def test_info(mock_file_exists_in_cloud):
    # Set up mock responses
    mock_file_exists_in_cloud.return_value = False

    with patch("radops.cli.data_lake.File.print_info") as print_info:
        assert not print_info.called
        result = runner.invoke(app, ["datalake", "info", "file_uid"])
        assert result.exit_code == 0
        assert "does not exist" in result.stdout
        assert not print_info.called

    mock_file_exists_in_cloud.return_value = True

    with patch("radops.cli.data_lake.File.print_info") as print_info:
        assert not print_info.called
        result = runner.invoke(app, ["datalake", "info", "file_uid"])
        assert result.exit_code == 0
        assert print_info.called


def test_download(mock_download, mock_file_exists_in_cloud):
    mock_exists_locally, mock_download_from_cloud = mock_download

    mock_file_exists_in_cloud.return_value = False
    assert not mock_download_from_cloud.called
    result = runner.invoke(app, ["datalake", "download", "file_uid"])
    assert result.exit_code == 0
    assert "is not in the datalake" in result.stdout
    assert not mock_download_from_cloud.called

    mock_file_exists_in_cloud.return_value = True
    mock_exists_locally.return_value = True
    result = runner.invoke(app, ["datalake", "download", "file_uid"])
    assert result.exit_code == 0
    assert "already exists locally" in result.stdout
    assert not mock_download_from_cloud.called

    mock_exists_locally.return_value = False
    result = runner.invoke(app, ["datalake", "download", "file_uid"])
    assert result.exit_code == 0
    assert mock_download_from_cloud.called


def test_purge_local_storage():
    with patch(
        "radops.cli.data_lake.get_unsynced_files"
    ) as get_unsynced_files:
        with patch("radops.cli.data_lake.get_local_path") as get_local_path:
            with patch("os.remove") as remove:
                get_unsynced_files.return_value = ["file1", "file2"]
                get_local_path.return_value = "path1"
                result = runner.invoke(
                    app, ["datalake", "purge-local-storage"]
                )
                assert result.exit_code == 0
                assert remove.called


def test_add():
    with patch("radops.cli.data_lake.add_from_url") as add_from_url:
        with patch("radops.cli.data_lake.add_local_file") as add_local_file:
            with patch("radops.cli.data_lake.os.path.exists") as exists:
                # make sure file exists check goes through
                exists.return_value = True
                assert add_from_url.call_count == 0
                assert add_local_file.call_count == 0

                result = runner.invoke(
                    app, ["datalake", "add", "http://url", "uid"]
                )
                assert result.exit_code == 0
                assert add_from_url.call_count == 1
                assert add_local_file.call_count == 0

                result = runner.invoke(
                    app, ["datalake", "add", "local_file", "uid", "--copy"]
                )
                assert result.exit_code == 0
                assert add_from_url.call_count == 1
                assert add_local_file.call_count == 1


def test_delete():
    with patch(
        "radops.cli.data_lake.File.get_all_downstream"
    ) as get_all_downstream:
        with patch("radops.cli.data_lake.File.delete") as delete:
            assert delete.call_count == 0
            get_all_downstream.return_value = []
            result = runner.invoke(app, ["datalake", "delete", "uid"])
            assert result.exit_code == 0
            assert delete.call_count == 1

            get_all_downstream.return_value = ["uid2"]
            result = runner.invoke(
                app, ["datalake", "delete", "uid"], input="n\n"
            )
            assert result.exit_code == 0
            assert delete.call_count == 1

            result = runner.invoke(
                app, ["datalake", "delete", "uid"], input="y\n"
            )
            assert result.exit_code == 0
            assert delete.call_count == 2


def test_local_path(settings_fixture):
    with patch(
        "radops.cli.data_lake.File.storage_path", new_callable=PropertyMock
    ) as storage_path, patch(
        "radops.cli.data_lake.file_exists_in_s3"
    ) as exists:
        exists.return_value = False
        storage_path.return_value = Path("local_path")
        result = runner.invoke(app, ["datalake", "local-path", "uid"])
        assert result.exit_code == 0
        assert "is not in the datalake" in result.stdout

        exists.return_value = True
        result = runner.invoke(app, ["datalake", "local-path", "uid"])
        assert result.exit_code == 0
        assert "has not been downloaded" in result.stdout

        m = MagicMock()
        m.exists.return_value = True
        storage_path.return_value = m
        result = runner.invoke(app, ["datalake", "local-path", "uid"])
        assert result.exit_code == 0
        assert "MagicMock" in result.stdout


def test_list_all_executors():
    with patch("radops.cli.jobs.executor.list_executors") as list_executors:
        list_executors.return_value = ["executor1", "executor2"]
        result = runner.invoke(app, ["executors", "list"])
        assert result.exit_code == 0
        assert "executor1" in result.stdout
        assert "executor2" in result.stdout


def test_add_executor():
    with patch("radops.cli.jobs.executor.add_executor") as add_executor:
        result = runner.invoke(
            app, ["executors", "add"], input="test\nhostname\nusername\n\n"
        )
        assert result.exit_code == 0
        assert add_executor.called


def test_view_executor():
    with patch("radops.cli.jobs.executor.get_executor") as get_executor:
        get_executor.return_value = "executor1"
        result = runner.invoke(app, ["executors", "view", "executor1"])
        assert result.exit_code == 0
        assert "executor1" in result.stdout


def test_setup(settings_fixture):
    assert not os.path.exists(settings_fixture.model_config["env_file"])
    result = runner.invoke(
        app,
        ["config", "setup"],
        input="test\nurl\nkey\nsecret key\ngcpproject\n",
    )
    assert result.exit_code == 0
    assert os.path.exists(settings_fixture.model_config["env_file"])
    assert "test" in open(settings_fixture.model_config["env_file"]).read()
    assert "url" in open(settings_fixture.model_config["env_file"]).read()
    assert "key" in open(settings_fixture.model_config["env_file"]).read()
    assert (
        "secret key" in open(settings_fixture.model_config["env_file"]).read()
    )

    result = runner.invoke(app, ["config", "setup"], input="n\n")
    assert result.exit_code == 0
    assert "configuration file already exists" in result.stdout
    assert "test" in open(settings_fixture.model_config["env_file"]).read()
    assert "url" in open(settings_fixture.model_config["env_file"]).read()
    assert "key" in open(settings_fixture.model_config["env_file"]).read()
    assert (
        "secret key" in open(settings_fixture.model_config["env_file"]).read()
    )

    result = runner.invoke(
        app,
        ["config", "setup"],
        input="y\notheremail\naddress\nk\nsk\ngcpproject\n",
    )
    assert result.exit_code == 0
    assert "configuration file already exists" in result.stdout
    assert "test" not in open(settings_fixture.model_config["env_file"]).read()
    assert (
        "otheremail" in open(settings_fixture.model_config["env_file"]).read()
    )
    assert "address" in open(settings_fixture.model_config["env_file"]).read()
