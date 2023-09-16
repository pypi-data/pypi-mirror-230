import inspect
import json
import os
import shutil
import stat
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import PosixPath
from typing import List, Set, Union
from urllib.parse import urljoin
from uuid import uuid4

import botocore
import rich
from rich.align import Align
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from radops import __version__, radops_print
from radops.data_lake import cloud_ops
from radops.settings import settings
from radops.utils import (
    get_file_path_relative_to_repo_root,
    get_last_commit_hash,
    get_package_version,
    get_repo_remote_origin,
)

_INSIDE_FILE_CREATOR = False


def is_write_mode(mode: str):
    return mode in ["w", "wb"]


def file_exists_in_data_lake(uid: str) -> bool:
    """If in local mode, then returns True if the file exists in local storage.
    Otherwise returns True if the file exists in local storage or it exists in
    the cloud.
    """
    f = File(uid)
    file_exists_locally = f.exists_locally()
    if settings.local_mode:
        return file_exists_locally
    else:
        return f.exists_in_cloud()


def delete_file(uid: str) -> None:
    f = File(uid)
    f.delete()


INFO_KEY = "radops-info"


@dataclass
class FunctionInfo:
    """stores function information"""

    module: str
    package_version: Union[str, None]
    name: str
    other_kwargs: dict

    # only if package is in a repo
    commit_hash: Union[str, None]
    file_path: Union[str, None]
    lineno: Union[int, None]
    remote: Union[str, None]

    dependencies: List[str]

    OUTPUT_UID_ARG_NAMES = {"output_uid", "output_uids"}

    @classmethod
    def from_fn_kwargs_dependencies(
        cls, fn: callable, kwargs: dict
    ) -> "FunctionInfo":
        abs_file_path = inspect.getfile(fn)
        commit_hash = get_last_commit_hash(abs_file_path)
        if commit_hash is not None:
            file_path = get_file_path_relative_to_repo_root(abs_file_path)
            lineno = inspect.findsource(fn)[1] + 2
            remote = get_repo_remote_origin(abs_file_path)
        else:
            file_path = None
            lineno = None
            remote = None
        return cls(
            module=fn.__module__,
            package_version=get_package_version(fn),
            name=fn.__name__,
            remote=remote,
            commit_hash=commit_hash,
            file_path=file_path,
            lineno=lineno,
            dependencies=[
                f.uid for f in kwargs.values() if isinstance(f, File)
            ],
            other_kwargs={
                k: v
                for k, v in kwargs.items()
                if k not in cls.OUTPUT_UID_ARG_NAMES
                and not isinstance(v, File)
            },
        )

    def github_url(self) -> Union[str, None]:
        """Return the URL of where the function definition is if the remote is
        on GitHub
        """
        if self.remote is None:
            return None
        if self.remote.startswith("git@github.com"):
            github_url = f"https://github.com/{self.remote.split('git@github.com:')[-1].split('.')[0]}/"
        elif self.remote.startswith("https://github.com"):
            github_url = self.remote.split(".git")[0] + "/"
        else:
            return None

        return urljoin(
            github_url,
            f"blob/{self.commit_hash}/{self.file_path}#L{self.lineno}",
        )


@dataclass
class FileInfo:
    radops_version: str
    originator: str
    created_by: FunctionInfo = None

    def json(self) -> str:
        ret = asdict(self)
        return json.dumps(ret)

    @classmethod
    def from_dict(cls, d) -> "FileInfo":
        if "created_by" in d:
            created_by_kwargs = d.pop("created_by")
            if created_by_kwargs is not None:
                fn_info = FunctionInfo(**created_by_kwargs)
            else:
                fn_info = None
        else:
            fn_info = None
        return cls(created_by=fn_info, **d)


def get_info_if_exists(uid: str) -> FileInfo:
    if uid is None:
        return None
    if settings.local_mode:
        return None
    try:
        obj = cloud_ops.s3.head_object(Bucket=settings.bucket_name, Key=uid)
    except botocore.exceptions.ClientError:
        return None

    metadata = obj["Metadata"]

    if INFO_KEY not in metadata:
        return None

    return FileInfo.from_dict(json.loads(obj["Metadata"][INFO_KEY]))


def get_dependencies(uid: str) -> List[str]:
    info = get_info_if_exists(uid)
    if info is None or info.created_by is None:
        return []
    return info.created_by.dependencies


def get_local_path(uid) -> PosixPath:
    return settings.local_storage / uid


def get_temp_storage_path() -> PosixPath:
    return get_local_path(str(uuid4()))


class File:
    def __init__(self, uid=None):
        self._temp_storage_path = None
        self.uid = uid
        self.info = get_info_if_exists(uid)

    def exists_locally(self) -> bool:
        return self.uid is not None and get_local_path(self.uid).exists()

    def exists_in_cloud(self) -> bool:
        if settings.local_mode:
            raise RuntimeError(
                "In local mode so cannot run `File.exists_in_cloud`"
            )
        return cloud_ops.file_exists_in_s3(self.uid)

    def download_from_cloud(self) -> None:
        cloud_ops.download_file_from_s3(self.uid, self.storage_path)
        # set the downloaded file to read only
        current = os.stat(self.storage_path).st_mode
        new = current & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        os.chmod(self.storage_path, new)

    def open(self, mode: str):
        """This is used similar to the `open` context mananger for files.

        If `mode` is a read mode then
            1. If the file exists in local storage then it will be opened from there.
            2. If the file does not exist in local storage but exists in the cloud, then it will be downloaded
               to local torage and then opened.
            3. If the file does not exist in local storage or the cloud, then a `RuntimeError` will be raised.

        If `mode` is a write mode then
            1. If the file exists in local storage then a `RuntimeError` is thrown since files in the data lake are immutable.
            2. Otherwise, a file will be created. If `self.uid` is already set then this will be created in local storage with that
               uid and then uploaded to the cloud. If `self.uid` is not set yet (which may happen when creating files via `file_creator`)
               then the file gets written to a temporary file and then as soon as `uid` is set it will be uploaded to the cloud.

        Parameters
        ----------
        mode
            must be one of "w", "wb", "r", "rb"
        """
        allowed_modes = ["w", "wb", "r", "rb"]
        if mode not in allowed_modes:
            raise ValueError(
                f"`mode` must be on of {allowed_modes} but got {mode}."
            )

        if is_write_mode(mode):
            if self.uid is not None:
                path = get_local_path(uid=self.uid)
                # check that file does not already exist
                if path.exists():
                    raise RuntimeError("cannot write a file twice")
            else:
                path = self._temp_storage_path = get_temp_storage_path()
        else:
            if self.uid is None:
                raise RuntimeError(
                    "Cannot read a `File` object that does not have a uid."
                )
            path = get_local_path(uid=self.uid)
            # if path does not exist then download from cloud
            if not path.exists():
                if settings.local_mode:
                    raise RuntimeError(
                        f"In local mode and file {self.uid} does not exist in local storage."
                    )
                if not cloud_ops.file_exists_in_s3(self.uid):
                    raise RuntimeError(
                        f"File {self.uid} does not exist locally or in the cloud."
                    )

                radops_print(
                    f"File {self.uid} does not exist locally, downloading from cloud."
                )
                cloud_ops.download_file_from_s3(self.uid, path)

        @contextmanager
        def _context_manager():
            """Simple wrapper around `open` that changes the exit behavior if the mode is
            a write mode. Namely, by uploading to cloud if `uid` is not None.
            """
            if is_write_mode(mode):
                os.makedirs(path.parent, exist_ok=True)
            fileobj = open(path, mode)
            yield fileobj
            fileobj.close()

            if is_write_mode(mode):
                if self.uid is not None and not _INSIDE_FILE_CREATOR:
                    self._maybe_upload_to_cloud()

        return _context_manager()

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid: str) -> None:
        """Sets the uid. If the file has been written to temp storage
        then this will move the file to the storage path corresponding to
        `uid` and then upload to the cloud.

        Raises
        ------
        RuntimeError
            if the uid has been set already
        """
        if hasattr(self, "_uid") and self._uid is not None:
            raise RuntimeError(
                "uid for a file cannot be changed after it has already been set"
            )
        self._uid = uid
        if self._temp_storage_path is not None:
            # move to storage path for its uid
            shutil.move(self._temp_storage_path, get_local_path(uid))
            self._temp_storage_path = None

    @property
    def storage_path(self) -> Union[PosixPath, None]:
        if self.uid is not None:
            return get_local_path(self.uid)
        else:
            return None

    def _maybe_upload_to_cloud(self):
        """If in local mode this will do nothing"""
        # import pdb

        # pdb.set_trace()
        if settings.local_mode:
            radops_print("Skipping upload to cloud since in local mode.")
        else:
            if cloud_ops.file_exists_in_s3(self.uid):
                raise RuntimeError(
                    f"File with uid '{self.uid}' already exists in the cloud."
                )
            radops_print("Adding to cloud.")
            if self.info is None:
                # then not from `file_creator`, so make info here
                self.info = FileInfo(
                    radops_version=__version__,
                    originator=settings.email,
                )

            metadata = {INFO_KEY: self.info.json()}

            cloud_ops.upload_file_to_s3(
                self.storage_path, self.uid, metadata=metadata
            )

    def _create_fn_panel(self) -> Panel:
        fn_table = Table(
            title="[b]creation method",
            title_justify="left",
            show_header=True,
            box=None,
        )
        fn_table.add_column()
        fn_table.add_column(style="b")

        fn_table.add_row(
            "function",
            f"[bold][bright_blue]{self.info.created_by.module}.{self.info.created_by.name}",
        )
        fn_table.add_row()
        for k, v in self.info.created_by.other_kwargs.items():
            fn_table.add_row(f"[i][b]{k}[/b][/i] argument", json.dumps(v))
        fn_panel = Panel.fit(fn_table)

        return fn_panel

    def _create_deps_panel(self, dependencies: List[str]) -> Panel:
        deps_table = Table(
            title="[b]input files",
            title_justify="left",
            show_header=True,
            box=None,
        )
        deps_table.add_column()
        for dep in dependencies:
            deps_table.add_row(f"[bold][bright_blue]{dep}")
        deps_panel = Align(
            Panel(deps_table),
            vertical="middle",
        )

        return deps_panel

    def print_info(self) -> None:
        """Prints graph representation"""
        if self.info is None:
            return

        is_atomic = self.info.created_by is None
        arrow = Align("⟶", vertical="middle")

        out_table = Table(
            title=f"[b]{'file' if is_atomic else 'output'}",
            title_justify="left",
            show_header=True,
            box=None,
        )
        out_table.add_column()
        out_table.add_column(style="b")
        out_table.add_row("uid", f"[bright_blue]{self.uid}")
        out_table.add_row("originator", self.info.originator)

        out_panel = Align(Panel(out_table), vertical="middle")

        if not is_atomic:
            fn_panel = self._create_fn_panel()

            dependencies = self.info.created_by.dependencies
            if len(dependencies):
                deps_panel = self._create_deps_panel(dependencies)

                columns = [deps_panel, arrow, fn_panel, arrow, out_panel]
            else:
                # no dependencies
                columns = [fn_panel, arrow, out_panel]
        else:
            columns = [out_panel]

        # columns.extend([fn_panel, arrow, out_panel])

        graph = Columns(columns, padding=(0, 1))

        rich.print(graph)
        if not is_atomic:
            rich.print(
                f"creation method code: {self.info.created_by.github_url()}"
            )
        rich.print(f"radops version: {self.info.radops_version}")

    def get_all_downstream(self) -> Set[str]:
        if settings.local_mode:
            return []
        # get all files that have an immediate dependency on `self`
        immediate_deps = cloud_ops.list_files_in_s3(
            filterer=lambda uid: self.uid in get_dependencies(uid)
        )
        ret = set(immediate_deps)
        for uid in immediate_deps:
            ret = ret.union(File(uid).get_all_downstream())
        return ret

    def delete(self, cascade=False) -> List[str]:
        """Deletes a file

        Parameters
        ----------
        cascade
            whether to also delete all downstream files. if there are downstream
            files and cascade is set to False then an error will be thrown

        Raises
        ------
        RuntimeError
            if the file has downstream dependents and cascade is set to False
        """

        downstream_uids = self.get_all_downstream()
        if len(downstream_uids) > 0 and not cascade:
            raise RuntimeError(
                f"File {self.uid} has the following downstream dependencies: {downstream_uids}."
                f" To preserve lineage, these also must be deleted if deleting {self.uid}."
                " This can be down by re-running the `delete` method and passing `cascade=True`."
            )

        def _del(uid):
            local_path = get_local_path(uid)
            if local_path.exists():
                os.remove(local_path)
            if (not settings.local_mode) and cloud_ops.file_exists_in_s3(uid):
                cloud_ops.delete_file_from_s3(uid)

        _del(self.uid)
        for uid in downstream_uids:
            _del(uid)

        return [self.uid] + list(downstream_uids)
