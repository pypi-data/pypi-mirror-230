from pydantic import BaseModel
from typing import List


class GetServices:
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        user: dict
        project: str

    class Outputs(BaseModel):
        services: List[str]

    def __call__(self, inputs: Inputs) -> Outputs:
        response = self.repo.retrieve_project(inputs.user, inputs.project)
        if response.status_code == 200:
            project = response.json()
            services = project["services"]
            names = [service["name"] for service in services]
            return self.Outputs(services=names)
        raise Exception(response.json()["detail"])
