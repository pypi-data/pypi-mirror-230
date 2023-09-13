import shutil
from pathlib import Path
import os


def init_project(project):
    # ask for project name
    # copy template
    template = Path(__file__).parent / "project-template"
    shutil.copytree(template, Path(project))
    # change name to project in spai.config.yaml
    config = Path(project) / "spai.config.yml"
    os.system(f"sed -i 's/project-template/{project}/g' {config}")
