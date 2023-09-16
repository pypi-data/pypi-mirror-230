from typing import List
from unittest.mock import Mock

import pytest

from radops.data_lake import File, FunctionInfo, file_creator
from radops.settings import Settings


def test_write_init_with_uid(settings_fixture):
    """check that we can create a File with a specified uid"""
    f = File("uid")
    with f.open("w") as fileobj:
        fileobj.write("testing")

    # check that the file actually got written to local storage
    local_path = settings_fixture.local_storage / "uid"
    assert local_path.exists()

    with open(local_path) as fileobj:
        assert fileobj.read() == "testing"

    # check we get an error if we try to set the uid again
    with pytest.raises(RuntimeError) as exc_info:
        f.uid = "new uid"
    assert "uid for a file cannot be changed" in str(exc_info)

    # check we get an error if we try to write again
    with pytest.raises(RuntimeError) as exc_info:
        with f.open("w") as fileobj:
            fileobj.write("blah")
    assert "cannot write" in str(exc_info)

    # check we can delete the local file
    f.delete()
    assert not local_path.exists()


def test_write_file_with_slashes_in_uid(settings_fixture: Settings):
    """check that we can create a File with slashes in the uid"""
    f = File("a/b/uid")
    with f.open("w") as fileobj:
        fileobj.write("testing")

    assert (settings_fixture.local_storage / "a").exists()
    assert (settings_fixture.local_storage / "a" / "b").exists()

    with open(settings_fixture.local_storage / "a" / "b" / "uid") as fileobj:
        assert fileobj.read() == "testing"


def test_file_creator_errors(settings_fixture):
    # check that we get an error if the number of `File` objects returned is different
    # then the length of `output_uids`

    @file_creator
    def fn3(f1: File, f2: File, output_uids: List[str]) -> List[File]:
        return [File("uid")]

    with pytest.raises(RuntimeError) as exc_info:
        fn3(f1=File("uid1"), f2=File("uid2"), output_uids=["uid3"])
    assert "to return files with uids ['uid3']" in str(exc_info)

    # check that we get an error if we call without keyword arguments
    with pytest.raises(RuntimeError) as exc_info:

        @file_creator
        def fn4(f1: File, a: str, output_uids: List[str]) -> File:
            return f1

        fn4(File("uid"), "asd", ["uid3"])

    assert "can only be called with keyword arguments" in str(exc_info)


def test_file_creator_single_file_explicit_uid(settings_fixture):
    """Test `file_creator` when method returns a single file"""
    uids = [f"uid{i}" for i in range(2)]
    for uid in uids:
        f = File(uid)
        with f.open("w") as fileobj:
            fileobj.write(f"data for {uid}")

    g = Mock()

    @file_creator
    def fn(f1: File, f2: File, s: str, output_uid: str) -> File:
        g()

        with f1.open("r") as f1_fileobj, f2.open("r") as f2_fileobj:
            data = f"{f1_fileobj.read()} {f2_fileobj.read()} {s}"

        f = File(output_uid)
        with f.open("w") as fileobj:
            fileobj.write(data)

        return f

    # sanity check
    assert g.call_count == 0

    def _run_and_verify_output():
        f_out = fn(
            f1=File("uid0"),
            f2=File("uid1"),
            s="additional text",
            output_uid="out_uid",
        )
        with f_out.open("r") as fileobj:
            assert (
                fileobj.read() == "data for uid0 data for uid1 additional text"
            )

    _run_and_verify_output()
    assert g.call_count == 1

    # now call `fn` again and since the file already exists `g` should not be called again
    _run_and_verify_output()
    assert g.call_count == 1


def test_file_creator_multiple_file_explicit_uids(settings_fixture):
    """Test `file_creator` when method returns a multiple files"""
    uids = [f"uid{i}" for i in range(2)]
    for uid in uids:
        f = File(uid)
        with f.open("w") as fileobj:
            fileobj.write(f"data for {uid}")

    g = Mock()

    @file_creator
    def fn(f1: File, f2: File, s: str, output_uids: List[str]) -> List[File]:
        g()

        with f1.open("r") as f1_fileobj, f2.open("r") as f2_fileobj:
            data = f"{f1_fileobj.read()} {f2_fileobj.read()} {s}"

        f1 = File(output_uids[0])
        with f1.open("w") as fileobj:
            fileobj.write(data)

        f2 = File(output_uids[1])
        with f2.open("w") as fileobj:
            fileobj.write("out_uid2 data")

        return [f1, f2]

    # sanity check
    assert g.call_count == 0

    def _run_and_verify_output():
        f1_out, f2_out = fn(
            f1=File("uid0"),
            f2=File("uid1"),
            s="additional text",
            output_uids=["out_uid1", "out_uid2"],
        )
        with f1_out.open("r") as fileobj:
            assert (
                fileobj.read() == "data for uid0 data for uid1 additional text"
            )
        with f2_out.open("r") as fileobj:
            assert fileobj.read() == "out_uid2 data"

    _run_and_verify_output()
    assert g.call_count == 1

    # now call `fn` again and since the file already exists `g` should not be called again
    _run_and_verify_output()
    assert g.call_count == 1


def test_file_creator_single_file_implicit_uid(settings_fixture):
    """Test `file_creator` when method returns a single file"""
    uids = [f"uid{i}" for i in range(2)]
    for uid in uids:
        f = File(uid)
        with f.open("w") as fileobj:
            fileobj.write(f"data for {uid}")

    g = Mock()

    @file_creator
    def fn(f1: File, f2: File, s: str) -> File:
        g()

        with f1.open("r") as f1_fileobj, f2.open("r") as f2_fileobj:
            data = f"{f1_fileobj.read()} {f2_fileobj.read()} {s}"

        f = File()
        with f.open("w") as fileobj:
            fileobj.write(data)

        return f

    # sanity check
    assert g.call_count == 0

    def _run_and_verify_output():
        f_out = fn(f1=File("uid0"), f2=File("uid1"), s="additional text")
        with f_out.open("r") as fileobj:
            assert (
                fileobj.read() == "data for uid0 data for uid1 additional text"
            )

    _run_and_verify_output()
    assert g.call_count == 1

    # now call `fn` again and since the file already exists `g` should not be called again
    _run_and_verify_output()
    assert g.call_count == 1


def test_function_info_github_url():
    fi = FunctionInfo(
        module="",
        package_version="",
        name="fn.name",
        other_kwargs={},
        commit_hash="hash",
        file_path="a/b/c.py",
        lineno=12,
        remote="git@github.com:org/repo.git",
        dependencies=[],
    )

    assert (
        fi.github_url() == "https://github.com/org/repo/blob/hash/a/b/c.py#L12"
    )

    fi = FunctionInfo(
        module="",
        package_version="",
        name="fn.name",
        other_kwargs={},
        commit_hash="hash",
        file_path="a/b/c.py",
        lineno=12,
        remote="https://github.com/org/repo.git",
        dependencies=[],
    )

    assert (
        fi.github_url() == "https://github.com/org/repo/blob/hash/a/b/c.py#L12"
    )


def test_external_package():
    def fn() -> File:
        pass

    fn.__module__ = "pkg.mod"
    fi = FunctionInfo.from_fn_kwargs_dependencies(fn, {})

    assert fi.module == "pkg.mod"
    assert fi.name == "fn"
