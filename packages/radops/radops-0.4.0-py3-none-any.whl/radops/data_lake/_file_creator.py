import copy
import inspect
import json
import os
import sys
from hashlib import md5
from typing import Any, Dict, List, Optional

from radops import __version__, radops_print
from radops.data_lake import (
    File,
    FileInfo,
    FunctionInfo,
    _file,
    cloud_ops,
    file_exists_in_data_lake,
)
from radops.settings import GENERATED_UIDS_PREFIX, settings


def _get_existing_generated_uids(fn_hash: str) -> List[str]:
    if settings.local_mode:
        files = [
            os.path.join(GENERATED_UIDS_PREFIX, f)
            for f in os.listdir(settings.generated_uids_path)
            if f.startswith(fn_hash)
        ]
    else:
        files = cloud_ops.list_files_in_s3(
            Prefix=os.path.join(GENERATED_UIDS_PREFIX, fn_hash)
        )

    return files


def _validate_and_check_if_output_files_exist(output_uids: List[str]) -> bool:
    """Makes sure that either every file with uid in `output_uids` exists in the data lake
    or none of them exist, and throws an error if not.

    Returns True if all output files exist and False if all output files do not exist
    """
    exists = []
    for uid in output_uids:
        if file_exists_in_data_lake(uid):
            exists.append(uid)

    if len(exists) == 0:
        return False

    if len(exists) != len(output_uids):
        raise RuntimeError(
            "Some output uids exist and others do not, but `output_uids` of `file_creator` functions"
            f" should either all exist or not exist yet. Files that are already in the data lake: {exists}. "
            f"Files that are not already in the data lake: {[uid for uid in output_uids if uid not in exists]}"
        )

    # TODO: if exists check that lineage is what it should be
    return True


def _save_info_locally(
    output_uids: List[str], metadata: FileInfo
) -> List[str]:
    """This called when there's an error. It goes through all uids in `output_uids`
    and if the file specified by a uid exists locally when the metadata is written
    the local metadata file, which can later be synced with the datalake. Returns the list
    of uids that exist
    """
    ret = []
    with open(settings.local_file_info, "a") as fileobj:
        for uid in output_uids:
            if File(uid).exists_locally():
                ret.append(ret)
                fileobj.write(f"{uid}\t{metadata.json()}\n")

    return ret


def _run_and_validate_output(
    fn: callable,
    kwargs: Dict[str, Any],
    output_uids: Optional[List[str]] = None,
    fn_hash: Optional[str] = None,
) -> List[File]:
    """Checks that output is a list of `File` objects of the same length as output_uids
    and throws a ValueError if not.
    """

    def _raise_error(bad_output: Any) -> None:
        raise ValueError(
            "Output of a file creator method must be `File` object or a list of `File` objects"
            f" but got output of type {type(bad_output)} from function {fn}"
        )

    fn_info = FunctionInfo.from_fn_kwargs_dependencies(fn=fn, kwargs=kwargs)

    metadata = FileInfo(
        radops_version=__version__,
        originator=settings.email,
        created_by=fn_info,
    )
    try:
        prev = _file._INSIDE_FILE_CREATOR
        _file._INSIDE_FILE_CREATOR = True
        output = fn(**kwargs)
    except Exception as e:
        computed_uids = _save_info_locally(output_uids, metadata)
        radops_print(
            f"Got an error during execution of {fn}. The files {computed_uids} exist in local storage."
        )
        raise e
    finally:
        _file._INSIDE_FILE_CREATOR = prev

    if not isinstance(output, (list, File)):
        _raise_error(output)

    singleton = False
    if isinstance(output, File):
        singleton = True
        output = [output]

    for out in output:
        if not isinstance(out, File):
            _raise_error(out)

    if fn_hash is not None:
        for i, out in enumerate(output):
            out.uid = os.path.join(GENERATED_UIDS_PREFIX, f"{fn_hash}_{i}")
    else:
        actual_output_uids = [out.uid for out in output]
        if len(output) != len(output_uids) or set(actual_output_uids) != set(
            output_uids
        ):
            raise RuntimeError(
                f"Expected function {fn} to return files with uids {output_uids}"
                f" but got uids {actual_output_uids}."
            )

    for output_file in output:
        output_file.info = metadata
        output_file._maybe_upload_to_cloud()

    return output[0] if singleton else output


def _validate_function_signature_return_if_singleton(fn: callable) -> bool:
    sig = inspect.signature(fn)

    allowed_return_types = [File, List[File]]
    if sys.version_info.minor >= 9:
        allowed_return_types.append(list[File])

    if sig.return_annotation not in allowed_return_types:
        raise RuntimeError(
            f"A file creator method must have return annotation that's one of {allowed_return_types}"
            f" but got {sig.return_annotation}"
        )

    expecting_singleton = sig.return_annotation == File
    return expecting_singleton


def hash_fn(
    fn: callable, kwargs: dict, ignore_args_for_hashing: List[str] = None
) -> str:
    ignore_args_for_hashing = ignore_args_for_hashing or []

    kwargs = copy.deepcopy(kwargs)

    input_uids = []
    non_file_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, File):
            input_uids.append(v.uid)
        else:
            non_file_kwargs[k] = v

    non_file_kwargs = json.dumps(non_file_kwargs, sort_keys=True)

    d = {
        "fn_module": fn.__module__,
        "fn_name": fn.__name__,
        "kwargs": non_file_kwargs,
        "input_uids": input_uids,
    }
    for k in ignore_args_for_hashing:
        if k in d["kwargs"]:
            d["kwargs"].pop(k)

    return md5(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()


def file_creator(fn) -> callable:
    """This creates a decorator that is used to wrap functions, `f`, that create new `Files`s from others."""

    expecting_singleton = _validate_function_signature_return_if_singleton(fn)

    def ret(*args, **kwargs):
        if len(args) != 0:
            raise RuntimeError(
                "Functions wrapped in `file_creator` can only be called with keyword arguments."
            )

        # generate_uids = False
        fn_hash = None
        if "output_uids" in kwargs:
            output_uids = kwargs["output_uids"]
            singleton = False
            if expecting_singleton:
                raise RuntimeError(
                    f"Expecting a singleton return based off of {fn}'s return annotation. Use `output_id` instead of `output_ids`."
                )
        elif "output_uid" in kwargs:
            output_uids = [kwargs["output_uid"]]
            singleton = True
            if not expecting_singleton:
                raise RuntimeError(
                    f"Not expecting a singleton return based off of {fn}'s return annotation. Use `output_ids` instead of `output_id`."
                )
        else:
            fn_hash = hash_fn(fn=fn, kwargs=kwargs)
            singleton = expecting_singleton
            output_uids = None

        # check and get any output_uids that begin with fn_hash
        if fn_hash:
            files = _get_existing_generated_uids(fn_hash)
            if len(files) > 0:
                output = [File(uid) for uid in files]
                if singleton:
                    output = output[0]
                return output
        # check if file exists in local storage, and if so skip
        # execution of the function
        elif _validate_and_check_if_output_files_exist(output_uids):
            radops_print(
                f"Skipping exection of {fn} since all files exist in the data lake."
            )
            output = [File(uid) for uid in output_uids]
            if singleton:
                output = output[0]

            return output

        return _run_and_validate_output(
            fn=fn, kwargs=kwargs, output_uids=output_uids, fn_hash=fn_hash
        )

    return ret
