from pathlib import Path

import requests


class File:
    config = None

    def __init__(self, client=None):
        self.config = client.get_config()

    def upload_application(self, file_category=None, project_name=None, file_path=None):
        path_object = Path(file_path)
        filename = path_object.name
        data = {
            "fileName": filename,
            "fileCategory": file_category,
            "userName": self.config.get("username"),
            "projectName": project_name
        }

        md5 = self.get_file_md5(filepath=file_path)
        data["md5sum"] = md5
        try:
            file_object = open(file_path, 'rb')
            files = {'file': file_object}
            response_message = self.__upload(data=data, files=files)
            file_object.close()
            return response_message
        except FileNotFoundError:
            return "Error: No such file or directory: " + filename

    def get_application_info(self, file_name=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
            "fileName": file_name
        }
        file_api_url = self.config.get("api_url") + "testexecute/files"
        response = requests.get(file_api_url, params=new_params, headers=new_headers)

        file_list = response.json()['data']['list']
        return_message = {}
        if len(file_list) == 0:
            return "Failure: File with name `" + file_name + "` not found."
        elif len(file_list) == 1:
            file_category = file_list[0]['fileCategory']
            if file_category == 'android-application':
                return_message = {"fileName": file_name,
                                  "fileCategory": file_list[0]['fileCategory'],
                                  "md5": file_list[0]['meta']['md5sum'],
                                  "fileURL": file_list[0]['meta']['s3Url'],
                                  "fileUUID": file_list[0]['uuid'],
                                  "packageName": file_list[0]['fileParameters']['packageName']
                                  }
            elif file_category == 'ios-application':
                return_message = {"fileName": file_name,
                                  "fileCategory": file_list[0]['fileCategory'],
                                  "md5": file_list[0]['meta']['md5sum'],
                                  "fileURL": file_list[0]['meta']['s3Url'],
                                  "fileUUID": file_list[0]['uuid']
                                  }
            elif file_category == 'android-test-application':
                return_message = {"fileName": file_name,
                                  "fileCategory": file_list[0]['fileCategory'],
                                  "md5": file_list[0]['meta']['md5sum'],
                                  "fileURL": file_list[0]['meta']['s3Url'],
                                  "fileUUID": file_list[0]['uuid'],
                                  "testCodePackageName": file_list[0]['fileParameters']['testCodePackageName'],
                                  "testRunnerName": file_list[0]['fileParameters']['testRunnerName']
                                  }
            elif file_category == 'ios-test-application':
                return_message = {"fileName": file_name,
                                  "fileCategory": file_list[0]['fileCategory'],
                                  "md5": file_list[0]['meta']['md5sum'],
                                  "fileURL": file_list[0]['meta']['s3Url'],
                                  "fileUUID": file_list[0]['uuid'],
                                  "XCTestRunFileUrl": file_list[0]['fileParameters']['xctestrunFileUrl']
                                  }
            return return_message

    def get_application_list(self, file_category=None, project_name=None):
        status_message = self.get_file_info_list(file_category=file_category, project_name=project_name)
        status_message_filtered = []
        try:
            for f in status_message:
                if f["fileCategory"] == "android-application" or f["fileCategory"] == "ios-application":
                    status_message_filtered.append(f)
            return status_message_filtered
        except TypeError:
            return "Error: Project Name or File Name doesn't exist"

    # Native Test Application

    def upload_native_test_application(self, file_category=None, project_name=None, file_path=None):
        status_message = self.upload_application(self, file_category=file_category,
                                                 project_name=project_name,
                                                 file_path=file_path)
        return status_message

    def get_native_test_application_info(self, file_name=None):
        status_message = self.get_application_info(file_name=file_name)
        return status_message


    def get_native_test_application_list(self, file_category=None, project_name=None):
        status_message = self.get_file_info_list(file_category=file_category, project_name=project_name)
        status_message_filtered = []
        try:
            for f in status_message:
                if f["fileCategory"] == "android-test-application" or f["fileCategory"] == "ios-test-application":
                    status_message_filtered.append(f)
            return status_message_filtered
        except TypeError:
            return "Error: Project Name Doesn't exist"

    def get_file_md5(self, filepath=None):
        import hashlib
        md5_hash = ''
        try:
            with open(filepath, "rb") as f:
                file_bytes = f.read()  # read file as bytes
                readable_hash = hashlib.md5(file_bytes).hexdigest()
                md5_hash = readable_hash
            return md5_hash
        except FileNotFoundError:
            return "Error: No such file or directory "


    def __upload(self, data=None, files=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}

        file_api_url = self.config.get("api_url") + "testexecute/files"
        file_name = data["fileName"]
        # Leg 1 - get the s3 file upload URL
        response = requests.post(file_api_url, json=data, headers=new_headers)

        if response.status_code == 200:
            if response.json()['status'] == 409:
                return "Error: File `" + file_name + "` already exists."
        else:
            return "Error: " + response.text

        s3_file_upload_url = response.json()['data']['uploadUrl']

        # Leg 2 - upload the file using s3 upload URL
        response = requests.put(s3_file_upload_url, files=files)

        if response.status_code == 200:
            return "Success: File `" + file_name + "` uploaded successfully."
        else:
            return "Failure: File `" + file_name + "` not uploaded."

    def get_file_info_list(self, file_category=None, project_name=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}

        if project_name is None:
            project_name = ""

        new_params = {
            "fileCategory": file_category,
            "projectName": project_name,
            "fileStatus": "processed"
        }
        file_api_url = self.config.get("api_url") + "testexecute/files"
        # Fetch list of files uploaded
        response = requests.get(file_api_url, params=new_params, headers=new_headers)

        file_list = response.json()['data']['list']
        return_message = []

        if len(file_list) > 0:
            for f in file_list:
                file_category = f['fileCategory']
                if file_category == 'android-application':
                    file_info = {"fileName": f['fileName'],
                                 "fileCategory": f['fileCategory'],
                                 "md5": f['meta']['md5sum'],
                                 "fileURL": f['meta']['s3Url'],
                                 "fileUUID": f['uuid'],
                                 "packageName": f['fileParameters']['packageName'],
                                 "projectName": project_name
                                 }
                    return_message.append(file_info)
                elif file_category == 'ios-application':
                    file_info = {"fileName": f['fileName'],
                                 "fileCategory": f['fileCategory'],
                                 "md5": f['meta']['md5sum'],
                                 "fileURL": f['meta']['s3Url'],
                                 "fileUUID": f['uuid'],
                                 "projectName": project_name
                                 }
                    return_message.append(file_info)
                elif file_category == 'android-test-application':
                    file_info = {"fileName": f['fileName'],
                                 "fileCategory": f['fileCategory'],
                                 "md5": f['meta']['md5sum'],
                                 "fileURL": f['meta']['s3Url'],
                                 "fileUUID": f['uuid'],
                                 "testCodePackageName": f['fileParameters']['testCodePackageName'],
                                 "testRunnerName": f['fileParameters']['testRunnerName'],
                                 "projectName": project_name
                                 }
                    return_message.append(file_info)
                elif file_category == 'ios-test-application':
                    file_info = {"fileName": f['fileName'],
                                 "fileCategory": f['fileCategory'],
                                 "md5": f['meta']['md5sum'],
                                 "fileURL": f['meta']['s3Url'],
                                 "fileUUID": f['uuid'],
                                 "XCTestRunFileUrl": f['fileParameters']['xctestrunFileUrl'],
                                 "projectName": project_name
                                 }
                    return_message.append(file_info)
            return return_message

    def delete_file(self, file_name=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}

        file_info = self.get_application_info(file_name=file_name)
        try:
            file_api_url = self.config.get("api_url") + "testexecute/files?fileId=" + file_info["fileUUID"]
        except TypeError:
            return "Failure: File `" + file_name + "` not available"
        response = requests.delete(file_api_url, headers=new_headers)
        try:
            if response.status_code == 200:
                return "Success: File `" + file_name + "` deleted successfully."
            else:
                return "Failure: File `" + file_name + "` not deleted."
        except TypeError:
            return "Failure: File `" + file_name + "` not delete"
