import importlib
import os
import subprocess
from typing import Union


def get_last_commit_hash(file_path: str) -> Union[str, None]:
    try:
        # Run the git rev-parse command to get the hash of the last commit
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=get_dir(file_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        commit_hash = result.stdout.strip()
        return commit_hash
    except subprocess.CalledProcessError:
        return None


def get_dir(file_path: str) -> str:
    ret = os.path.dirname(file_path)
    if ret == "":
        return "."
    return ret


def get_repo_root(file_path: str) -> Union[str, None]:
    try:
        # Run the git rev-parse command to get the hash of the last commit
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=get_dir(file_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        repo_root = result.stdout.strip()
        return repo_root
    except subprocess.CalledProcessError:
        return None


def get_repo_remote_origin(file_path: str) -> Union[str, None]:
    try:
        # Run the git rev-parse command to get the hash of the last commit
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=get_dir(file_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        repo_root = result.stdout.strip()
        return repo_root
    except subprocess.CalledProcessError:
        return None


def get_file_path_relative_to_repo_root(file_path: str) -> Union[str, None]:
    repo_root = get_repo_root(file_path)
    if repo_root is None:
        return None
    return os.path.relpath(file_path, repo_root)


def get_package_version(fn: callable) -> Union[str, None]:
    try:
        pkg_name = fn.__module__.split(".")[0]
        importlib.import_module(pkg_name).__version__
    except Exception:
        return None
