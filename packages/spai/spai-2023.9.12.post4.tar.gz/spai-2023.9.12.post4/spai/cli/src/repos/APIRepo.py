import requests
import os


class APIRepo:
    # def __init__(self, url=os.getenv("SPAI_API_URL", "https://spai.api.dev.earthpulse.ai/")):
    def __init__(self, url=os.getenv("SPAI_API_URL", "http://localhost:8000/")):
        self.url = url

    def login(self):
        return requests.get(self.url + "auth/login")

    def token(self, code):
        return requests.get(self.url + "auth/token?code=" + code)

    def logout_url(self):
        response = requests.get(self.url + "auth/logout")
        return response.json()["logout_url"]

    def get_headers(self, user):
        return {"Authorization": "Bearer " + user["id_token"]}

    def retrieve_projects(self, user):
        return requests.get(
            self.url + "projects", headers=self.get_headers(user)
        ).json()

    def retrieve_project(self, user, project):
        return requests.get(
            self.url + f"projects/{project}", headers=self.get_headers(user)
        )

    def run_service(self, user, service, files, data):
        response = requests.post(
            self.url + f"run/{service}",
            data=data,
            files=files,
            headers=self.get_headers(user),
        )
        if response.status_code == 200:
            return response.text
        return "Something went wrong.\n" + response.json()["detail"]

    def schedule_service(self, user, service, files, data):
        response = requests.post(
            self.url + f"schedule/{service}",
            data=data,
            files=files,
            headers=self.get_headers(user),
        )
        if response.status_code == 200:
            return response.text
        return "Something went wrong.\n" + response.json()["detail"]

    def stop_service(self, user, project, service, name):
        response = requests.post(
            self.url + f"stop/{service}",
            json={"project": project, "name": name},
            headers=self.get_headers(user),
        )
        if response.status_code == 200:
            return f"Stopped."
        return "Something went wrong.\n" + response.json()["detail"]

    def get_logs(self, user, project, service, name):
        response = requests.post(
            self.url + f"logs/{service}",
            json={"project": project, "name": name},
            headers=self.get_headers(user),
        )
        if response.status_code == 200:
            return response.json()
        return "Something went wrong.\n" + response.json()["detail"]
