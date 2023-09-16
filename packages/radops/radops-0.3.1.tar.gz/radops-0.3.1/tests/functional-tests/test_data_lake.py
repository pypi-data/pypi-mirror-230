import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import List
from unittest.mock import Mock

import pytest

import radops
from radops.data_lake import (
    File,
    FileInfo,
    FunctionInfo,
    add_local_file,
    cloud_ops,
    file_creator,
    list_local_files,
)
from radops.data_lake._file import get_last_commit_hash, get_repo_remote_origin
from radops.settings import Settings, settings


@pytest.fixture
def objects_to_cleanup():
    objects = []
    yield objects
    for obj in objects:
        cloud_ops.delete_file_from_s3(obj)


@pytest.fixture
def settings_fixture(tmp_path: Path):
    """Fixture use to changing local_storage to a temporary folder and sets
    local mode to true (so no interaction with s3)
    """
    settings.base_path = tmp_path
    settings.validate_base_path(settings.base_path)
    settings.email = "user@domain.com"
    if settings.local_mode:
        raise RuntimeError(
            "To run functional-tests/test_data_lake.py s3 settings must be set."
        )

    return settings


def assert_file_infos_equal_mod_lineno(fi1: FileInfo, fi2: FileInfo) -> None:
    d1 = asdict(fi1)
    d2 = asdict(fi2)

    for d in [d1, d2]:
        assert isinstance(d["created_by"].pop("lineno"), int)

    assert d1 == d2


def test_write_init(settings_fixture: Settings, objects_to_cleanup: List[str]):
    """check that we can create a File with a specified uid"""

    # sanity check file is not already in the cloud
    assert not cloud_ops.file_exists_in_s3("uid")

    f = File("uid")
    with f.open("w") as fileobj:
        fileobj.write("testing")

    # check the file got uploaded
    assert cloud_ops.file_exists_in_s3("uid")

    # check we get an error if we try to set the uid again
    with pytest.raises(RuntimeError) as exc_info:
        f.uid = "new uid"
    assert "uid for a file cannot be changed" in str(exc_info)

    # check that deletion works
    f.delete()
    assert not cloud_ops.file_exists_in_s3("uid")
    assert not f.storage_path.exists()
    objects_to_cleanup.append("uid")


def test_cannot_write_if_exists_in_cloud(
    tmp_path: Path, settings_fixture: Settings, objects_to_cleanup: list
):
    """This tests that if a file with a uid already exists in the cloud
    then an error will be throne after trying to write with a `File` with that uid.
    """

    # add some data to the cloud with name "uid"
    tempfile = tmp_path / "fname"
    with open(tempfile, "w") as f:
        f.write("some text")
    cloud_ops.upload_file_to_s3(tempfile, "uid")

    # check we get an error if we create a `File` object with uid "uid"
    # and then try to write to it
    f = File("uid")
    with pytest.raises(RuntimeError) as exc_info:
        with f.open("w") as fileobj:
            fileobj.write("data")
    assert "File with uid 'uid' already exists" in str(exc_info)

    objects_to_cleanup.append("uid")


def test_read_file(
    tmp_path: Path, settings_fixture: Settings, objects_to_cleanup: list
):
    """test that if a file exists in the cloud and we call read, then
    we will load the file from the cloud
    """
    # create a file in s3 directly (i.e. not through radops.data_lake.File, which would
    # also put it in local storage)
    tempfile = tmp_path / "fname"
    with open(tempfile, "w") as f:
        f.write("some text")
    cloud_ops.upload_file_to_s3(tempfile, "uid")

    # sanity check file does not exist locally
    assert not (settings.local_storage / "uid").exists()

    f = File("uid")
    with f.open("r") as fileobj:
        assert fileobj.read() == "some text"

    # check file does exists locally
    assert (settings.local_storage / "uid").exists()

    objects_to_cleanup.append("uid")

    # check we get an error if we try to read a file that does not exist
    f = File("otheruid")

    with pytest.raises(RuntimeError) as exc_info:
        with f.open("r") as fileobj:
            pass
    assert "does not exist locally or in the cloud" in str(exc_info)


def test_file_creator_with_dependencies(
    settings_fixture: Settings,
    objects_to_cleanup: list,
    capsys: pytest.CaptureFixture[str],
):
    """tests file creator with a function that has `File` dependencies"""
    uids = [f"uid{i}" for i in range(2)]
    objects_to_cleanup.extend(uids + ["out_uid"])

    for uid in uids:
        f = File(uid)
        with f.open("w") as fileobj:
            fileobj.write(f"data for {uid}")

    g = Mock()

    @file_creator
    def fn(f1: File, f2: File, s: str, output_uid: str) -> File:
        g()
        f = File(output_uid)
        with f.open("w") as fileobj:
            fileobj.write("data")

        return f

    assert g.call_count == 0

    f = fn(
        f1=File("uid0"), f2=File("uid1"), s="a string", output_uid="out_uid"
    )
    assert f.info is not None

    assert g.call_count == 1
    # check the metadata is actually in s3
    obj = cloud_ops.s3.head_object(Bucket=settings.bucket_name, Key="out_uid")

    s3_meta = json.loads(obj["Metadata"]["radops-info"])
    s3_meta["created_by"].pop("lineno")
    assert s3_meta == {
        "created_by": {
            "module": "test_data_lake",
            "package_version": None,
            "name": "fn",
            "other_kwargs": {"s": "a string"},
            "dependencies": ["uid0", "uid1"],
            "remote": get_repo_remote_origin("test_data_lake.py"),
            "commit_hash": get_last_commit_hash("test_data_lake.py"),
            "file_path": "tests/functional-tests/test_data_lake.py",
        },
        "radops_version": radops.__version__,
        "originator": settings_fixture.email,
    }

    # grad the file again and check metadata is there
    f = File("out_uid")

    assert_file_infos_equal_mod_lineno(
        f.info,
        FileInfo(
            created_by=FunctionInfo(
                module="test_data_lake",
                package_version=None,
                name="fn",
                dependencies=["uid0", "uid1"],
                other_kwargs={"s": "a string"},
                commit_hash=get_last_commit_hash("test_data_lake.py"),
                remote=get_repo_remote_origin("test_data_lake.py"),
                file_path="tests/functional-tests/test_data_lake.py",
                lineno=144,
            ),
            radops_version=radops.__version__,
            originator=settings_fixture.email,
        ),
    )

    # check `print_lineage` gives output
    f.print_info()
    captured = capsys.readouterr()
    assert "test_data_lake.fn" in captured.out
    assert "uid0" in captured.out
    assert "uid1" in captured.out
    assert "a string" in captured.out
    assert "input" in captured.out

    # run the function again and check that the count hasn't increased
    assert g.call_count == 1

    # now delete locally and run again, checking that the call count hasn't
    # increased and that the file gets downloaded
    assert f.exists_locally()
    os.remove(f.storage_path)
    assert not f.exists_locally()

    fn(f1=File("uid0"), f2=File("uid1"), s="a string", output_uid="out_uid")
    assert g.call_count == 1


def test_file_creator_with_implicit_uids(
    settings_fixture: Settings,
    objects_to_cleanup: list,
    capsys: pytest.CaptureFixture[str],
):
    """tests file creator with a function that has `File` dependencies"""
    uids = [f"uid{i}" for i in range(2)]
    objects_to_cleanup.extend(uids)

    for uid in uids:
        f = File(uid)
        with f.open("w") as fileobj:
            fileobj.write(f"data for {uid}")

    g = Mock()

    @file_creator
    def fn(f1: File, f2: File, s: str) -> File:
        g()
        f = File()
        with f.open("w") as fileobj:
            fileobj.write("data")

        return f

    assert g.call_count == 0

    f = fn(f1=File("uid0"), f2=File("uid1"), s="a string")
    objects_to_cleanup.append(f.uid)
    assert f.info is not None

    assert g.call_count == 1

    # grab the file again and check metadata is there
    f = File(f.uid)
    assert_file_infos_equal_mod_lineno(
        f.info,
        FileInfo(
            created_by=FunctionInfo(
                module="test_data_lake",
                package_version=None,
                name="fn",
                dependencies=["uid0", "uid1"],
                other_kwargs={"s": "a string"},
                commit_hash=get_last_commit_hash("test_data_lake.py"),
                remote=get_repo_remote_origin("test_data_lake.py"),
                file_path="tests/functional-tests/test_data_lake.py",
                lineno=144,
            ),
            radops_version=radops.__version__,
            originator=settings_fixture.email,
        ),
    )

    # check `print_lineage` gives output
    f.print_info()
    captured = capsys.readouterr()
    assert "test_data_lake.fn" in captured.out
    assert "uid0" in captured.out
    assert "uid1" in captured.out
    assert "a string" in captured.out
    assert "input" in captured.out

    # run the function again and check that the count hasn't increased
    assert g.call_count == 1

    # now delete locally and run again, checking that the call count hasn't
    # increased and that the file gets downloaded
    assert f.exists_locally()
    os.remove(f.storage_path)
    assert not f.exists_locally()

    fn(f1=File("uid0"), f2=File("uid1"), s="a string")
    assert g.call_count == 1

    # now call again with a different parameter for s and make sure the function gets run again
    f = fn(f1=File("uid0"), f2=File("uid1"), s="a different string")
    objects_to_cleanup.append(f.uid)
    assert g.call_count == 2

    # now call again with a different parameter for f1 and make sure the function gets run again
    f = fn(f1=File("uid3"), f2=File("uid1"), s="a different string")
    objects_to_cleanup.append(f.uid)
    assert g.call_count == 3


def test_file_creator_with_implicit_uids_mult_return(
    settings_fixture: Settings,
    objects_to_cleanup: list,
    capsys: pytest.CaptureFixture[str],
):
    """tests file creator with a function that has `File` dependencies"""
    uids = [f"uid{i}" for i in range(2)]
    objects_to_cleanup.extend(uids)

    for uid in uids:
        f = File(uid)
        with f.open("w") as fileobj:
            fileobj.write(f"data for {uid}")

    g = Mock()

    @file_creator
    def fn(f1: File, f2: File, s: str) -> List[File]:
        g()
        f1 = File()
        f2 = File()
        with f1.open("w") as fileobj:
            fileobj.write("data")

        with f2.open("w") as fileobj:
            fileobj.write("other data")

        return [f1, f2]

    assert g.call_count == 0

    f1, f2 = fn(f1=File("uid0"), f2=File("uid1"), s="a string")
    objects_to_cleanup.extend([f1.uid, f2.uid])
    assert f2.info is not None

    assert g.call_count == 1

    # grab the file again and check metadata is there
    f = File(f2.uid)
    assert_file_infos_equal_mod_lineno(
        f.info,
        FileInfo(
            created_by=FunctionInfo(
                module="test_data_lake",
                package_version=None,
                name="fn",
                dependencies=["uid0", "uid1"],
                other_kwargs={"s": "a string"},
                commit_hash=get_last_commit_hash("test_data_lake.py"),
                remote=get_repo_remote_origin("test_data_lake.py"),
                file_path="tests/functional-tests/test_data_lake.py",
                lineno=144,
            ),
            radops_version=radops.__version__,
            originator=settings_fixture.email,
        ),
    )

    # check `print_lineage` gives output
    f2.print_info()
    captured = capsys.readouterr()
    assert "test_data_lake.fn" in captured.out
    assert "uid0" in captured.out
    assert "uid1" in captured.out
    assert "a string" in captured.out
    assert "input" in captured.out

    # run the function again and check that the count hasn't increased
    assert g.call_count == 1

    # now delete locally and run again, checking that the call count hasn't
    # increased and that the file gets downloaded
    assert f2.exists_locally()
    os.remove(f2.storage_path)
    assert not f2.exists_locally()

    fn(f1=File("uid0"), f2=File("uid1"), s="a string")
    assert g.call_count == 1

    # now call again with a different parameter for s and make sure the function gets run again
    f1, f2 = fn(f1=File("uid0"), f2=File("uid1"), s="a different string")
    objects_to_cleanup.extend([f1.uid, f2.uid])
    assert g.call_count == 2

    # now call again with a different parameter for f1 and make sure the function gets run again
    f1, f2 = fn(f1=File("uid3"), f2=File("uid1"), s="a different string")
    objects_to_cleanup.extend([f1.uid, f2.uid])
    assert g.call_count == 3


def test_file_creator_without_dependencies(
    settings_fixture: Settings,
    objects_to_cleanup: list,
    capsys: pytest.CaptureFixture[str],
):
    """tests file creator with a function that has no `File` dependencies"""
    objects_to_cleanup.append("out_uid2")

    @file_creator
    def fn2(s: str, output_uids: List[str]) -> List[File]:
        f = File(output_uids[0])
        with f.open("w") as fileobj:
            fileobj.write("data")

        return [f]

    fn2(s="anotherstring", output_uids=["out_uid2"])
    f = File("out_uid2")
    assert_file_infos_equal_mod_lineno(
        f.info,
        FileInfo(
            created_by=FunctionInfo(
                module="test_data_lake",
                package_version=None,
                name="fn2",
                dependencies=[],
                other_kwargs={"s": "anotherstring"},
                commit_hash=get_last_commit_hash("test_data_lake.py"),
                remote=get_repo_remote_origin("test_data_lake.py"),
                file_path="tests/functional-tests/test_data_lake.py",
                lineno=205,
            ),
            radops_version=radops.__version__,
            originator=settings_fixture.email,
        ),
    )

    f.print_info()
    captured = capsys.readouterr()
    assert "test_data_lake.fn2" in captured.out
    assert "out_uid2" in captured.out
    assert "anotherstring" in captured.out
    assert "input files" not in captured.out


def test_upload_from_local_copy(
    settings_fixture: Settings, objects_to_cleanup: list, tmp_path: Path
):
    objects_to_cleanup.append("uid")

    local_path = os.path.join(tmp_path, "local_file.txt")
    with open(local_path, "w") as fileobj:
        fileobj.write("some data")
    f = add_local_file(path=local_path, output_uid="uid", copy=True)

    assert f.info == FileInfo(
        created_by=FunctionInfo(
            module="radops.data_lake",
            package_version=None,
            name="add_local_file",
            dependencies=[],
            other_kwargs={"path": local_path, "copy": True},
            commit_hash=get_last_commit_hash("test_data_lake.py"),
            remote=get_repo_remote_origin("test_data_lake.py"),
            file_path="radops/data_lake/__init__.py",
            lineno=31,
        ),
        radops_version=radops.__version__,
        originator=settings_fixture.email,
    )

    # verify we have a copy by changing `local_path` and
    # checking we do not see a change in the file in local storage
    with open(local_path, "w") as fileobj:
        fileobj.write("new data")

    with f.open("r") as fileobj:
        assert fileobj.read() == "some data"


def test_upload_from_local_move(
    settings_fixture: Settings, objects_to_cleanup: list, tmp_path: Path
):
    objects_to_cleanup.append("uid")

    local_path = os.path.join(tmp_path, "local_file.txt")
    with open(local_path, "w") as fileobj:
        fileobj.write("some data")
    f = add_local_file(path=local_path, output_uid="uid", copy=False)

    assert f.info == FileInfo(
        created_by=FunctionInfo(
            module="radops.data_lake",
            package_version=None,
            name="add_local_file",
            dependencies=[],
            other_kwargs={"path": local_path, "copy": False},
            commit_hash=get_last_commit_hash("test_data_lake.py"),
            remote=get_repo_remote_origin("test_data_lake.py"),
            file_path="radops/data_lake/__init__.py",
            lineno=31,
        ),
        radops_version=radops.__version__,
        originator=settings_fixture.email,
    )

    assert not os.path.exists(local_path)


def test_file_creator_on_error(settings_fixture: Settings, tmp_path: Path):
    """tests that file info is saved locally in the case that an error happens during
    function execution.
    """

    @file_creator
    def fn(s: str, output_uids: List[str]) -> List[File]:
        f1 = File(output_uids[0])
        with f1.open("w") as fileobj:
            fileobj.write("data")
        raise RuntimeError("example error")
        f2 = File(output_uids[0])
        with f2.open("w") as fileobj:
            fileobj.write("other data")

        return f1, f2

    with pytest.raises(RuntimeError) as exc_info:
        fn(s="a string", output_uids=["uid1", "uid2"])
    assert "example error" in str(exc_info)

    # uid1 should exist locally but uid2 shouldn't. and neither
    # should be in the cloud
    assert File("uid1").exists_locally()
    assert not File("uid1").exists_in_cloud()

    assert not File("uid2").exists_locally()
    assert not File("uid2").exists_in_cloud()

    # check local file infos is what it should be
    with open(settings_fixture.local_file_info) as f:
        infos = f.readlines()

    assert len(infos) == 1
    uid, info = infos[0].split("\t")
    assert uid == "uid1"
    info_dict = json.loads(info)
    info_dict["created_by"].pop("lineno")
    assert info_dict == {
        "radops_version": radops.__version__,
        "originator": "user@domain.com",
        "created_by": {
            "module": "test_data_lake",
            "package_version": None,
            "name": "fn",
            "dependencies": [],
            "other_kwargs": {"s": "a string"},
            "commit_hash": get_last_commit_hash("test_data_lake.py"),
            "remote": get_repo_remote_origin("test_data_lake.py"),
            "file_path": "tests/functional-tests/test_data_lake.py",
        },
    }


def test_cascade_delete(settings_fixture: Settings, objects_to_cleanup: list):
    objects_to_cleanup.extend(["uid1", "in_uid", "out_uid"])

    @file_creator
    def fn_no_deps(s: str, output_uid: str) -> File:
        f = File(output_uid)
        with f.open("w") as fileobj:
            fileobj.write("data")

        return f

    f = fn_no_deps(s="a str", output_uid="uid1")

    assert f.exists_in_cloud()
    assert f.exists_locally()

    f.delete()
    assert not f.exists_in_cloud()
    assert not f.exists_locally()

    @file_creator
    def fn_with_deps(s: str, in_file: File, output_uid: str) -> File:
        f = File(output_uid)
        with f.open("w") as fileobj:
            fileobj.write("data")

        return f

    in_file = File("in_uid")
    with in_file.open("w") as fileobj:
        fileobj.write("data")

    out_file = fn_with_deps(s="", in_file=in_file, output_uid="out_uid")
    assert out_file.exists_in_cloud()
    assert out_file.exists_locally()
    assert in_file.exists_in_cloud()
    assert in_file.exists_locally()
    # we should get an error since out_uid is downstream from in_uid
    with pytest.raises(RuntimeError) as exc_info:
        in_file.delete()
    assert "has the following downstream" in str(exc_info)

    # now check cascade delete
    in_file.delete(cascade=True)
    assert not out_file.exists_in_cloud()
    assert not out_file.exists_locally()
    assert not in_file.exists_in_cloud()
    assert not in_file.exists_locally()

    # now repeat the above and check that if we first delete out_uid then
    # we can delete in_uid without having to cascade
    in_file = File("in_uid")
    with in_file.open("w") as fileobj:
        fileobj.write("data")

    out_file = fn_with_deps(s="", in_file=in_file, output_uid="out_uid")
    assert out_file.exists_in_cloud()
    assert out_file.exists_locally()
    assert in_file.exists_in_cloud()
    assert in_file.exists_locally()
    out_file.delete()
    in_file.delete()
    assert not out_file.exists_in_cloud()
    assert not out_file.exists_locally()
    assert not in_file.exists_in_cloud()
    assert not in_file.exists_locally()


def test_folder_structure(
    settings_fixture: Settings, objects_to_cleanup: list
):
    paths = ["a/b/c", "a/b/d", "a/h", "a/i", "e/f", "g"]
    objects_to_cleanup.extend(paths)
    for p in paths:
        with File(p).open("w") as fileobj:
            fileobj.write("some data")

    assert cloud_ops.list_files_and_folders() == (["g"], ["a", "e"])
    assert cloud_ops.list_files_and_folders("a") == (["h", "i"], ["b"])
    assert cloud_ops.list_files_and_folders("a/") == (["h", "i"], ["b"])
    assert cloud_ops.list_files_and_folders("a/b") == (["c", "d"], [])
    assert cloud_ops.list_files_and_folders("a/b/") == (["c", "d"], [])

    assert set(list_local_files()) == set(paths)
