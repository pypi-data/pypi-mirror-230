import os
import json

from ..project import get_services, stop_service, run_service, schedule_service


def setup_files(item_type, dir):
    files = {
        item_type: open(
            dir / f'main.{"ipynb" if item_type == "notebook" else "py"}', "rb"
        ),
        "requirements": open(dir / "requirements.txt", "rb")
        if "requirements.txt" in os.listdir(dir)
        else None,
        "env": open(dir / ".env", "rb") if ".env" in os.listdir(dir) else None,
    }
    return files


def run_item(user, item, dir, typer, config, rebuild, item_type):
    item_dir = dir / item.name
    typer.echo(f"Running item '{item.name}'...")
    data = {
        "name": item.name,
        "project": config.project,
        "rebuild": rebuild,
        "command": item.command,
    }
    if item_type == "api" or item_type == "ui":
        data["port"] = item.port
    if item_type == "ui":
        data["command"] = item.command
        if item.env:
            data["env_vars"] = json.dumps(item.env)
    if item_type != "ui":
        data["storage"] = item.storage
    files = setup_files(item_type, item_dir)
    return run_service(user, item_type, files, data)


def schedule_item(user, item, dir, typer, config, rebuild, item_type):
    item_dir = dir / item.name
    typer.echo(f"Setting up cronjob for item '{item.name}'...")
    files = setup_files(item_type, item_dir)
    data = {
        "name": item.name,
        "project": config.project,
        "run_every": item.run_every,
        "storage": item.storage,
        "rebuild": rebuild,
    }
    return schedule_service(user, item_type, files, data)


def run_script_or_notebook(user, item, dir, typer, config, rebuild, item_type):
    if item.run_on_start:
        run_item(user, item, dir, typer, config, rebuild, item_type)
    if item.run_every:
        schedule_item(user, item, dir, typer, config, rebuild, item_type)


def check_item(user, item, project, services, typer, item_type):
    name = f"{item_type}.{item.name}"
    if name in services:
        typer.echo(f"Service '{name}' already deployed.")
        typer.echo(f"Stopping ...")  # confirm?
        stop_service(user, project, item_type, item.name)


def deploy_cloud(user, dir, config, typer, rebuild):
    typer.echo(f"Deploying...")
    try:
        services = get_services(user, config.project)
    except Exception as e:
        services = []  # project not found
    if config.scripts:
        typer.echo(f"Deploying scripts...")
        for script in config.scripts:
            check_item(user, script, config.project, services, typer, "script")
            message = run_script_or_notebook(
                user, script, dir / "scripts", typer, config, rebuild, "script"
            )
            typer.echo(message)
    if config.notebooks:
        typer.echo(f"Deploying notebooks...")
        for notebook in config.notebooks:
            check_item(user, notebook, config.project, services, typer, "notebook")
            run_script_or_notebook(
                user, notebook, dir / "notebooks", typer, config, rebuild, "notebook"
            )
    if config.apis:
        typer.echo(f"Deploying APIs...")
        for api in config.apis:
            check_item(user, api, config.project, services, typer, "api")
            run_item(user, api, dir / "apis", typer, config, rebuild, "api")
    if config.uis:
        typer.echo(f"Deploying UIs...")
        for ui in config.uis:
            check_item(user, ui, config.project, services, typer, "ui")
            run_item(user, ui, dir / "uis", typer, config, rebuild, "ui")
    # TODO: delete running services that no longer are in config???
