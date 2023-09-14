import json

import requests


class Project:
    config = None

    def __init__(self, client=None):
        self.config = client.get_config()

    def create_project(self, project_name=None, project_description=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        data = {
            "name": project_name,
            "description": project_description
        }
        project_api_url = self.config.get("api_url") + "testexecute/projects"
        response = requests.post(project_api_url, json=data, headers=new_headers)
        if response.json()["status"] == 200 and response.json()["message"] == "Success":
            return "Success"
        elif response.json()["status"] == 409 and response.json()["message"] == "Project already exists":
            return "Failure: Project with "+project_name+" already exists."

    def get_project_info(self, project_name=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
            "name": project_name
        }
        project_api_url = self.config.get("api_url") + "testexecute/projects"
        # Fetch list of projects
        response = requests.get(project_api_url, params=new_params, headers=new_headers)
        project_list = response.json()["data"]["list"]
        return_message = {}

        if response.status_code == 200 and len(project_list) == 1:
            response_project_name = project_list[0]["name"]
            if response_project_name == project_name:
                response_project_description = project_list[0]["description"]
                response_project_uuid = project_list[0]["uuid"]
                return_message["projectName"] = response_project_name
                return_message["projectDescription"] = response_project_description
                return_message["projectUUID"] = response_project_uuid
                return return_message
        elif response.status_code == 200 and len(project_list) == 0:
            return "Failure: Project with name `" + project_name + "` not found."

    def delete_project(self, project_name=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        project_info = self.get_project_info(project_name=project_name)
        if project_info == "Failure: Project with name `" + project_name + "` not found.":
            return project_info
        else:
            delete_project_url = self.config.get("api_url") + "testexecute/projects?projectId=" + project_info["projectUUID"]
            response = requests.delete(delete_project_url, headers=new_headers)
            if response.json()["status"] == 200 and response.json()["message"] == "Success":
                return "Success"

    def get_project_list(self):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}

        project_api_url = self.config.get("api_url") + "testexecute/projects"
        # Fetch list of projects
        response = requests.get(project_api_url, headers=new_headers)
        project_list = response.json()["data"]["list"]

        response_project_list = []
        if response.status_code == 200 and len(project_list) > 0:
            for p in project_list:
                project_info = {"projectName": p["name"],
                                "projectDescription": p["description"],
                                "projectUUID": p["uuid"]}
                response_project_list.append(project_info)
            return response_project_list
        elif response.status_code == 200 and len(project_list) == 0:
            return "Failure: Project list is empty."
