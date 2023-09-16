from abc import ABC, abstractmethod
from typing import Any, Dict

import docker
import rich
from fabric import Connection
from rich.markup import escape
from rich.progress import Progress

from radops.settings import settings


def _show_push_progress(line, progress):
    tasks = {}

    status_to_colors = {
        "Preparing": "pink3",
        "Waiting": "yellow",
        "Pushing": "green",
        "Layer already exists": "blue",
    }

    if "status" not in line:
        return
    status = line["status"]
    if status not in status_to_colors:
        rich.print(f"[cyan]{escape(status)}")
        return

    val = f"[{status_to_colors[status]}][{status} {line['id']}]"

    if val not in tasks.keys():
        tasks[val] = progress.add_task(
            f"{val}", total=line["progressDetail"].get("total")
        )
    else:
        progress.update(
            tasks[val], completed=line["progressDetail"]["current"]
        )


def build_image(
    image_name: str, path: str, pull: bool = False, nocache: bool = False
) -> None:
    client = docker.APIClient()

    stream = client.build(
        path=path,
        tag=image_name,
        quiet=False,
        decode=True,
        platform="linux/amd64",
        pull=pull,
        nocache=nocache,
    )
    for x in stream:
        if "stream" in x:
            print(f"{x['stream']}", end="")


def push_image(image_name: str) -> None:
    client = docker.APIClient()
    with Progress() as progress:
        stream = client.push(
            image_name,
            auth_config={
                "username": settings.container_registry_username,
                "password": settings.container_registry_password.get_secret_value(),
            },
            stream=True,
            decode=True,
        )

        for line in stream:
            _show_push_progress(line, progress)


class DockerJobExecutor(ABC):
    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def pull(self, image_name: str):
        pass

    @abstractmethod
    def run(
        self,
        image_name: str,
        name: str,
        command: Any,
        env_variables: Dict[str, Any],
    ) -> str:
        pass

    @abstractmethod
    def logs(self, container_name: str):
        pass


class LocalDockerJobExecutor(DockerJobExecutor):
    def __init__(self) -> None:
        self.docker_client = docker.APIClient()

    def login(self):
        self.docker_client.login(
            username=settings.container_registry_username,
            password=settings.container_registry_password.get_secret_value(),
            registry=settings.container_repository,
        )

    def pull(self, image_name: str):
        repository, tag = image_name.split(":")
        self.docker_client.pull(repository=repository, tag=tag)

    def run(
        self,
        image_name: str,
        name: str,
        command: Any = None,
        env_variables: Dict[str, Any] = None,
    ) -> None:
        env_variables = env_variables or {}
        # for some reason can't use the lower level APIClient for this? so we use `DockerClient` instead
        client = docker.from_env()
        client.containers.run(
            image_name,
            command=command,
            name=name,
            detach=True,
            environment=env_variables,
        )

    def logs(self, container_name: str) -> str:
        return self.docker_client.logs(container_name).decode()


class RemoteDockerJobExecutor(DockerJobExecutor):
    def __init__(self, conn: Connection, docker_path: str):
        self.conn = conn
        self.docker_path = docker_path

    def login(self):
        self.conn.run(
            f"echo {settings.container_registry_password.get_secret_value()} | {self.docker_path} login ghcr.io -u {settings.container_registry_username} --password-stdin"
        )

    def pull(self, image_name: str):
        self.conn.run(f"{self.docker_path} pull {image_name}")

    def run(
        self,
        image_name: str,
        name: str,
        command: Any = None,
        env_variables: Dict[str, Any] = None,
    ):
        cmd_str = f"{self.docker_path} run --name {name}"
        if env_variables is not None:
            for key, val in env_variables.items():
                cmd_str += f' -e "{key}={val}"'

        cmd_str += f" -d {image_name}"
        if command is not None:
            cmd_str += f" {command}"
        self.conn.run(cmd_str)

    def logs(self, container_name: str) -> str:
        return self.conn.run(
            f"{self.docker_path} logs {container_name}", hide=True
        ).stdout
