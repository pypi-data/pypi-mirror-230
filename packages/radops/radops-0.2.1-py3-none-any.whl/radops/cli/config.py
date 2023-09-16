import os
import shutil
import time

import rich
import typer
from rich.table import Table

from radops import settings

from .common import _y_n_prompt_loop

app = typer.Typer()


@app.command(name="view")
def view():
    """Displays current `radops` configuration"""
    table = Table("setting", "value")
    for k, v in settings.model_dump().items():
        table.add_row(k, str(v))
    rich.print(table)


@app.command(name="setup")
def setup():
    """Sets up `radops` configuration"""
    env_path = settings.model_config["env_file"]
    backup_path = None
    if os.path.exists(env_path):
        _y_n_prompt_loop(
            f"configuration file already exists at {settings.model_config['env_file']}, overwrite?"
        )
        backup_path = str(env_path) + time.strftime("%Y%m%d-%H%M%S")
        rich.print(f"Backing up existing config to {backup_path}")
        shutil.move(env_path, backup_path)

    try:
        settings_dict = {}
        settings_dict["email"] = typer.prompt("Your e-mail address")
        settings_dict["s3_endpoint_url"] = typer.prompt("S3 URL")
        settings_dict["aws_access_key_id"] = typer.prompt("Access key")
        settings_dict["aws_secret_access_key"] = typer.prompt(
            "Secret access key", hide_input=True
        )
        settings_dict["gcp_project_id"] = typer.prompt("GCP project ID")
    except Exception as e:
        if backup_path is not None:
            rich.print("[yellow]Restoring configuration")
            shutil.move(backup_path, env_path)

        if not isinstance(e, KeyboardInterrupt):
            raise e

    with open(env_path, "w") as f:
        for k, v in settings_dict.items():
            f.write(f"{k}={v}\n")

    rich.print(
        f"For connecting to GCP, you will need to download a JSON key to {settings.gcp_key}."
    )
