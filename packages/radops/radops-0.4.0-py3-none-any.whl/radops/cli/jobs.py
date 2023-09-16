from datetime import datetime
from typing import Optional

import rich
import typer
from typing_extensions import Annotated

from radops.jobs import executor, gcp
from radops.settings import settings

app = typer.Typer()


@app.command(name="list")
def list_all_executors():
    """list all executors"""
    rich.print(executor.list_executors())


@app.command(name="add")
def add_executor():
    name = typer.prompt("Executor name")
    hostname = typer.prompt("hostname")
    username = typer.prompt("username")
    dockerpath = typer.prompt("dockerpath", default="/usr/bin/docker")

    rich.print(f"Adding executor {name}...")
    executor.add_executor(
        name,
        type=executor.ExecutorType.MANUALLY_CONFIGURED,
        hostname=hostname,
        username=username,
        dockerpath=dockerpath,
    )


@app.command(name="delete")
def delete_executor(name: str):
    if name not in executor.list_executors():
        rich.print(f"Executor '{name}' does not exist.")
        raise typer.Exit(1)
    executor.remove_executor(name)
    rich.print(f"Deleted executor '{name}'.")


@app.command(name="connect")
def connect_to_executor(name: str):
    """Prints command to use to connect to the specified executor via ssh"""
    if name == "local":
        rich.print("Cannot call `connect` with the local executor.")
        raise typer.Exit(1)
    exc = executor.get_executor(name)
    rich.print(
        f"Run [b][blue]ssh {exc.username}@{exc.hostname}[/blue][/b] to connect to the remote machine."
    )


@app.command(name="view")
def view_executor(name: str):
    """view the specified executor"""
    rich.print(executor.get_executor(name))


@app.command(name="run")
def run_job(
    executor_name: str,
    path: str,
    command: Annotated[Optional[str], typer.Argument()] = None,
):
    """run a job on the specified executor"""
    job_id = executor.job_pipeline(
        executor.get_executor(executor_name), path, command
    )
    rich.print(f"Started job with id {job_id}")
    rich.print(
        f"You can view the logs with 'radops executors logs {executor_name} {job_id}'"
    )


@app.command(name="logs")
def get_logs(executor_name: str, job_id: str):
    """get logs for the specified job"""
    try:
        rich.print(
            executor.get_logs(executor.get_executor(executor_name), job_id)
        )
    except Exception as e:
        rich.print(
            "Received an error while fetching logs. Please verify the job exists on the executor."
        )
        rich.print(f"Error: {e}")


gcp_app = typer.Typer()
app.add_typer(gcp_app, name="gcp")


@gcp_app.command(name="list-templates")
def list_templates():
    """list all templates"""
    rich.print(gcp.list_templates())


@gcp_app.command(name="create")
def create_executor(
    template_name: str, name: Annotated[Optional[str], typer.Argument()] = None
):
    if template_name not in gcp.list_templates():
        rich.print(f"Template '{template_name}' does not exist.")
        raise typer.Exit(1)
    if name is None:
        name = f"gcp-{template_name}-{settings.email.split('@')[0].replace('.', '')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    gcp.create_gcp_executor(name, template_name)
