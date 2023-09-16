import json
import random
import string
from dataclasses import dataclass
from typing import Any, Dict, List

from fabric import Connection

import radops
from radops.jobs.docker import (
    DockerJobExecutor,
    LocalDockerJobExecutor,
    RemoteDockerJobExecutor,
    build_image,
    push_image,
)
from radops.settings import settings


@dataclass
class Executor:
    hostname: str = None
    username: str = None
    dockerpath: str = "/usr/bin/docker"

    def get_connection(self) -> Connection:
        return (
            Connection(self.hostname, user=self.username)
            if not self.is_local
            else None
        )

    @property
    def is_local(self):
        return self.hostname is None

    def get_docker_job_executor(self) -> DockerJobExecutor:
        if self.is_local:
            return LocalDockerJobExecutor()
        return RemoteDockerJobExecutor(
            conn=self.get_connection(), docker_path=self.dockerpath
        )


_EXECUTORS: Dict[str, Executor] = None


def load_all_executors() -> None:
    with open(settings.executors_file) as f:
        executors = json.load(f)

    global _EXECUTORS
    _EXECUTORS = {k: Executor(**v) for k, v in executors.items()}


def list_executors() -> List[str]:
    return list(_EXECUTORS.keys())


def add_executor(name: str, **kwargs) -> None:
    with open(settings.executors_file) as f:
        executors = json.load(f)

    try:
        Executor(**kwargs)
    except KeyError:
        raise ValueError("Got invalid arguments for `Executor`.")
    executors[name] = kwargs

    with open(settings.executors_file, "w") as f:
        json.dump(executors, f)

    load_all_executors()


def remove_executor(name: str) -> None:
    with open(settings.executors_file) as f:
        executors = json.load(f)

    if name in executors:
        del executors[name]

    with open(settings.executors_file, "w") as f:
        json.dump(executors, f)


def get_executor(name: str) -> Executor:
    return _EXECUTORS[name]


load_all_executors()


def create_job_id() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))


def image_name_from_job_id(job_id: str):
    return f"{settings.container_repository}:{job_id}"


def job_build_and_push(path: str) -> str:
    job_id = create_job_id()
    image_name = image_name_from_job_id(job_id)

    radops.radops_print(f"Building image {image_name}")
    build_image(image_name, path)
    radops.radops_print(f"Pushing image {image_name}")
    push_image(image_name)

    return job_id


def remote_login_pull_run(
    executor: Executor, job_id: str, command: Any = None
) -> None:
    image_name = image_name_from_job_id(job_id)
    docker_job_exec = executor.get_docker_job_executor()
    docker_job_exec.login()
    radops.radops_print(
        f"Pulling image {image_name} to remote machine {executor.hostname}"
    )
    docker_job_exec.pull(image_name)
    docker_job_exec.run(image_name, name=job_id, command=command)


def job_pipeline(executor: Executor, path: str, command: Any = None) -> str:
    job_id = job_build_and_push(path)
    remote_login_pull_run(executor, job_id=job_id, command=command)

    return job_id


def get_logs(executor: Executor, job_id: str) -> str:
    docker_job_exec = executor.get_docker_job_executor()
    return docker_job_exec.logs(job_id)
