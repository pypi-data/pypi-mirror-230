from pydantic import BaseModel
from typing import Union, List
from pathlib import Path


class ScriptConfig(BaseModel):
    name: str
    command: Union[str, None] = None
    run_every: Union[int, None] = None  # seconds (in cloud minutes)
    run_on_start: bool = True
    storage: Union[str, None] = None  # folder to bind in cloud
    type: str = "script"


class NotebookConfig(BaseModel):
    name: str
    command: Union[str, None] = None
    run_every: Union[int, None] = None  # seconds
    run_on_start: bool = True
    storage: Union[str, None] = None  # folder to bind in cloud
    type: str = "notebook"


class APIConfig(BaseModel):
    name: str
    command: Union[str, None] = None
    port: int = 8000
    host: str = "0.0.0.0"
    storage: Union[str, None] = None  # folder to bind in cloud
    type: str = "api"


class UIConfig(BaseModel):
    name: str
    command: str  # steamlit, javascript, ...
    port: int = 3000
    env: dict = {}  # can accept the name of another service as a url placeholder
    type: str = "ui"


class Config(BaseModel):
    dir: Path
    project: Union[str, None] = None
    scripts: Union[List[ScriptConfig], None] = None
    notebooks: Union[List[NotebookConfig], None] = None
    apis: Union[List[APIConfig], None] = None
    uis: Union[List[UIConfig], None] = None

    # iterator for all the services
    def __iter__(self):
        if self.scripts:
            for script in self.scripts:
                yield script
        if self.notebooks:
            for notebook in self.notebooks:
                yield notebook
        if self.apis:
            for api in self.apis:
                yield api
        if self.uis:
            for ui in self.uis:
                yield ui

    def type2folder(self, type):
        return type + "s"
