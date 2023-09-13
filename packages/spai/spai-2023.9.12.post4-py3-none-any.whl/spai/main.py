import typer
import os
import sys
from pathlib import Path

# Add the cli directory to the Python path
spai_cli_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(spai_cli_dir))

from cli.commands import auth as _auth

from cli.src.usecases.auth import auth
from cli.src.usecases.project import (
    init_project,
    install_reqs,
    get_services,
    stop_service,
    get_logs,
)
from cli.src.usecases.run import (
    run_local,
    deploy_cloud,
    load_and_validate_config,
)

app = typer.Typer()
app.add_typer(_auth.app, name="auth")


@app.command()
def init():
    project = typer.prompt("Project name")
    init_project(project)
    typer.echo(f"Project {project} created")


@app.command()
def list(
    project: str,
):
    try:
        user = auth()
        services = get_services(user, project)
        if len(services) == 0:
            return typer.echo(f"No services running in project '{project}'.")
        return typer.echo(f"Services in project '{project}': {services}")
    except Exception as e:
        return typer.echo(e)


@app.command()
def run(
    dir: Path,
):
    dir = Path(dir).resolve()
    config = load_and_validate_config(dir, typer)
    return run_local(dir, config, typer)


@app.command()
def deploy(
    dir: Path,
    rebuild: bool = typer.Option(False, "-r", "--rebuild"),  # force rebuild image
):
    dir = Path(dir).resolve()
    config = load_and_validate_config(dir, typer, True)
    user = auth()
    return deploy_cloud(user, dir, config, typer, rebuild)


@app.command()
def stop(
    project: str,
):
    try:
        user = auth()
        services = get_services(user, project)
        if len(services) == 0:
            return typer.echo(f"No services running in project '{project}'.")
        for service in services:
            service_type, name = service.split(".")
            typer.echo(f"Stopping service '{name}'...")
            stop_service(user, project, service_type, name)
        return typer.echo(f"Stopped all scripts in project '{project}'.")
    except Exception as e:
        return typer.echo(e)


@app.command()
def logs(
    project: str,
    service: str,
):
    service, name = service.split(".")
    user = auth()
    logs = get_logs(user, project, service, name)
    typer.echo(logs)


@app.command()
def install(
    dir: Path = typer.Option(
        Path.cwd(), "-d", "--dir", help="Directory containing the spai.yaml file"
    )
):
    config = load_and_validate_config(dir, typer)
    install_reqs(config, typer.echo)


if __name__ == "__main__":
    app()
