import os
import schedule
import time
from multiprocessing import Process


def run_item(item, command):
    if item.command:
        os.system(item.command)
    else:
        os.system(command)


def run_script(args):
    script, dir, typer = args
    typer.echo(f"Running script '{script.name}'...")
    os.chdir(dir)  # change to project dir
    run_item(script, f"python scripts/{script.name}/main.py")


def run_notebook(args):
    notebook, dir, typer = args
    typer.echo(f"Running notebook '{notebook.name}'...")
    os.chdir(dir / "notebooks" / notebook.name)  # necessary ???
    run_item(
        notebook,
        f"papermill main.ipynb output.ipynb",
    )
    # papermill can execute notebooks and save output in S3
    # papermill can execute notebooks with params


def run_api(api, dir, port, host):
    os.chdir(dir)
    os.system(f"python apis/{api.name}/main.py --port {port} --host {host}")


def run_ui(ui, dir, api_urls):
    os.chdir(dir)
    cmd = ""
    for name, value in ui.env.items():
        if value in api_urls:
            cmd += f"export {name}={api_urls[value]}; "
    cmd += ui.command
    os.system(cmd)


def run_schdule():
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_local(dir, config, typer):
    typer.echo(f"Deploying locally...")
    keep_alive = False
    processes = []
    if config.scripts:
        for script in config.scripts:
            # the order affects in the execution of the scheduled tasks
            typer.echo(f"Deploying scripts...")
            # # TODO: reqs, env
            if script.run_on_start:
                run_script((script, dir, typer))
            if script.run_every:
                keep_alive = True
                schedule.every(script.run_every).minutes.do(
                    run_script, (script, dir, typer)
                )  # if a task goes after another than takes more time than the scheduled time, it will have to wait
    if config.notebooks:
        typer.echo(f"Deploying notebooks...")
        for notebook in config.notebooks:
            # TODO: reqs, env
            if notebook.run_on_start:
                run_notebook((notebook, dir, typer))
            if notebook.run_every:
                keep_alive = True
                schedule.every(notebook.run_every).minutes.do(
                    run_notebook, (notebook, dir, typer)
                )
    api_urls = {}
    if config.apis:
        typer.echo(f"Deploying apis...")
        for api in config.apis:
            typer.echo(f"Running api '{api.name}'...")
            # TODO: reqs, env
            # load_dotenv(f"{dir}/apis/{api.name}/.env")
            p = Process(target=run_api, args=(api, dir, api.port, api.host))
            p.start()
            processes.append(p)
            # save api_urls in case UIs need them
            api_urls[f"api.{api.name}"] = f"http://{api.host}:{api.port}"
    if config.uis:
        typer.echo(f"Deploying uis...")
        for ui in config.uis:
            typer.echo(f"Running ui '{ui.name}'...")
            # TODO: reqs, env
            # load_dotenv(f"{dir}/apis/{api.name}/.env")
            p = Process(target=run_ui, args=(ui, dir, api_urls))
            p.start()
            processes.append(p)
    typer.echo(f"Project '{config.project}' deployed.")
    if keep_alive:
        p = Process(target=run_schdule)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    return
