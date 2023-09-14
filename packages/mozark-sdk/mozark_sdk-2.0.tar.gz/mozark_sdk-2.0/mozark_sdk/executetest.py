import json
from pathlib import Path
import requests


class TestExecute:
    config = None
    client = None

    def __init__(self, client=None):
        self.config = client.get_config()
        self.client = client

    def execute_test_now(self,
                         project_name=None,
                         test_framework=None,
                         application_file_name=None,
                         test_application_file_name=None,
                         devices=None,
                         test_configuration=None,
                         test_parameters=None
                         ):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        test_parameters_req = {
            "testType": "app-automation",
            "maxTestDuration": test_parameters["maxTestDuration"],
            "testFramework": test_framework,
            "projectName": project_name,
            "packageName": ""
        }
        application_url = self.client.get_application_info(file_name=application_file_name)["fileURL"]
        test_application_url = self.client.get_native_test_application_info(file_name=test_application_file_name)[
            "fileURL"]

        data = {
            "deviceId": devices,
            "testConfiguration": test_configuration,
            "scheduleConfiguration": {},
            "testAction": {
                "pre": {},
                "post": {}
            },
            "testParameters": test_parameters_req,
            "applicationUrl": application_url,
            "testApplicationUrl": test_application_url,
            "executionType": "NOW"
        }

        print(data)

        test_api_url = self.config.get("api_url") + "testexecute/schedules"
        response = requests.post(test_api_url, json=data, headers=new_headers)
        if response.status_code == 200:
            try:
                schedule_id = {
                    "scheduleId": response.json()["data"]["scheduleId"]
                }
                test_api_url = self.config.get("api_url") + "testexecute/schedules"
                response = requests.get(test_api_url, params=schedule_id, headers=new_headers)
                print(response.json())
                schedule_details = response.json()['data']['list'][0]['testExecutions']
                testIds = []
                for tests in schedule_details:
                    testIds.append(tests['uuid'])
                response = {
                    "message": "Success: Executed/Scheduled successfully",
                    "testId": testIds
                }
                return response
            except Exception as e:
                print(e)
                return {"statusCode:": response.status_code, "message": response.text}

        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_info(self, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "analytics/tests/" + test_id + "/info"
        # Fetch info of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            test_list = test_list['body']
            formatted_response = {
                "projectName": test_list['projectName'],
                # "testFramework": test_list['extra']['testType'],
                "applicationFileName": test_list['appVersion'],
                "testApplicationFileName": test_list['scriptName'],
                "device": test_list['deviceName'],
                "testStartTime": test_list['testStartTime'],
                "testEndTime": test_list['testEndTime'],
                "testUUID": test_list['uuid']['testId'],
                "testStatus": test_list['testStatus']
                # "testStatusDescription": ""
            }
            return formatted_response
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def schedule_test_executions(self,
                                 project_name=None,
                                 test_framework=None,
                                 application_file_name=None,
                                 test_application_file_name=None,
                                 devices=None,
                                 test_configuration=None,
                                 test_parameters=None,
                                 start_date_time=None,
                                 end_date_time=None,
                                 interval=None
                                 ):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        test_parameters_req = {
            "testType": "app-automation",
            "maxTestDuration": test_parameters["maxTestDuration"],
            "testFramework": test_framework,
            "projectName": project_name,
            "packageName": ""
        }
        application_url = self.client.get_application_info(file_name=application_file_name)["fileURL"]
        test_application_url = self.client.get_native_test_application_info(file_name=test_application_file_name)[
            "fileURL"]

        data = {
            "deviceId": devices,
            "testConfiguration": test_configuration,
            "scheduleConfiguration": {
                "startTime": start_date_time,
                "endTime": end_date_time,
                "interval": interval
            },
            "testAction": {
                "pre": {},
                "post": {}
            },
            "testParameters": test_parameters_req,
            "applicationUrl": application_url,
            "testApplicationUrl": test_application_url,
            "executionType": "SCHEDULE"
        }

        print(data)
        test_api_url = self.config.get("api_url") + "testexecute/schedules"
        response = requests.post(test_api_url, json=data, headers=new_headers)
        if response.status_code == 200:
            try:
                schedule_id = {
                    "scheduleId": response.json()["data"]["scheduleId"]
                }
                test_api_url = self.config.get("api_url") + "testexecute/schedules"
                response = requests.get(test_api_url, params=schedule_id, headers=new_headers)
                print(response.json())
                scheduleId = response.json()['data']['list'][0]['uuid']
                testIds = response.json()['data']['list'][0]['testExecutions']
                testId_list = []
                for tests in testIds:
                    test_new = {"testUUID": tests['uuid'], "testStartDateTime": tests['testScheduledTime']}
                    testId_list.append(test_new)

                formatted_response = {
                    "message": "Success: Executed/Scheduled successfully",
                    "scheduleUUID": scheduleId,
                    "testRuns": testId_list
                }
                return formatted_response
            except Exception as e:
                print(e.with_traceback())
                return {"statusCode:": response.status_code, "message": response.text}
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_schedule_info(self, schedule_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        schedule_id = {
            "scheduleId": schedule_id
        }
        test_api_url = self.config.get("api_url") + "testexecute/schedules"
        response = requests.get(test_api_url, params=schedule_id, headers=new_headers)
        print(response.json())
        try:
            response = response.json()['data']['list'][0]
            testInfo = []
            for tests in response['testExecutions']:
                test_details = {
                    "device": tests['devices'][0],
                    "testStartTime": tests['testScheduledTime'],
                    "testEndTime": "",
                    "testUUID": tests['uuid'],
                    "testStatus": tests['testStatus'],
                    "testStatusDescription": ""
                }
                testInfo.append(test_details)

            formatted_response = {
                "scheduleUUID": response['uuid'],
                "scheduleStartTime": response['scheduleConfiguration']['startTime'],
                "scheduleEndTime": response['scheduleConfiguration']['endTime'],
                "testInterval": response['scheduleConfiguration']['interval'],
                "testConfiguration": response['testExecutions'][0]['testConfiguration'],
                "testParameters": response['testExecutions'][0]['testParameters'],
                "projectName": response['testExecutions'][0]['testParameters']['projectName'],
                "testFramework": response['testExecutions'][0]['testParameters']['testFramework'],
                "applicationFileName": response['testExecutions'][0]['applicationUrl'],
                "testApplicationFileName": response['testExecutions'][0]['testApplicationUrl'],
                "testInfo": testInfo
            }

            return formatted_response
        except IndexError:
            return "Failure: schedule id " + schedule_id["scheduleId"] + " doesn't exists."

    def get_test_schedule_list(self, from_date_time=None, to_date_time=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        params = {
            #        "startTime": from_date_time,
            #        "endTime": to_date_time
        }
        test_api_url = self.config.get("api_url") + "testexecute/schedules"
        response = requests.get(test_api_url, params=params, headers=new_headers)
        complete_response = []
        for res in response.json()['data']['list']:
            testInfo = []
            for tests in res['testExecutions']:
                test_details = {
                    "device": tests['devices'][0],
                    "testStartTime": tests['testScheduledTime'],
                    "testEndTime": "",
                    "testUUID": tests['uuid'],
                    "testStatus": tests['testStatus'],
                    "testStatusDescription": ""
                }
                testInfo.append(test_details)
            formatted_response = {
                "scheduleUUID": res['uuid'],
                "scheduleStartTime": res['scheduleConfiguration']['startTime'],
                "scheduleEndTime": res['scheduleConfiguration']['endTime'],
                "testInterval": res['scheduleConfiguration']['interval'],
                "testConfiguration": res['testExecutions'][0]['testConfiguration'],
                "testParameters": res['testExecutions'][0]['testParameters'],
                "projectName": res['testExecutions'][0]['testParameters']['projectName'],
                "testFramework": res['testExecutions'][0]['testParameters']['testFramework'],
                "applicationFileName": res['testExecutions'][0]['applicationUrl'],
                "testApplicationFileName": res['testExecutions'][0]['testApplicationUrl'],
                "testInfo": testInfo
            }
            complete_response.append(formatted_response)
        return complete_response

    def execute_test(self, client=None, device_list=None, test_configuration={}, schedule_configuration={},
                     test_parameters={},
                     execution_type=None, application_url=None, application_test_url=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        data = {
            "deviceId": device_list,
            "testConfiguration": test_configuration,
            "scheduleConfiguration": schedule_configuration,
            "testAction": {
                "pre": {},
                "post": {}
            },
            "testParameters": test_parameters,
            "applicationUrl": application_url,
            "testApplicationUrl": application_test_url,
            "executionType": execution_type
        }
        test_api_url = self.config.get("api_url") + "testexecute/schedules"
        response = requests.post(test_api_url, json=data, headers=new_headers)
        if response.status_code == 200:
            my_resp = json.loads(response.text)
            my_resp = my_resp['data']
            return my_resp
        else:
            return {"statusCode:": response.status_code, "message": response.text}
        # return response.status_code, response.text

    def list_schedules(self, client=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "testexecute/schedules"
        # Fetch list of schedules
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            my_resp = json.loads(response.text)
            my_resp = my_resp['data']['list']
            return my_resp
        else:
            return {"statusCode:": response.status_code, "message": response.text}
        # return response.status_code, response.text

    def delete_schedule(self, schedule_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
            "scheduleId": schedule_id
        }
        test_api_url = self.config.get("api_url") + "testexecute/schedules"
        # Delete schedule
        response = requests.delete(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            my_resp = json.loads(response.text)
            my_resp = my_resp["message"]
            return my_resp
        else:
            return {"statusCode:": response.status_code, "message": response.text}
        # return response.text

    def abort_test(self, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        data = {
            "testId": test_id
        }
        test_api_url = self.config.get("api_url") + "testexecute/tests"
        # abort test
        response = requests.put(test_api_url, json=data, headers=new_headers)
        return response.text

    def schedule_test(self, client=None, device_list=None, schedule_configuration={}, test_configuration={},
                      test_parameters={}, application_url=None, application_test_url=None):
        # schedule_configuration = {
        #     "startTime": start_time,
        #     "endTime": end_time,
        #     "interval": interval
        # }
        # test_parameters = {
        #     "maxTestDuration": max_duration,
        #     "testFramework": test_framework,
        #     "projectName": project_name
        # }
        execution_type = "SCHEDULE"
        status_message = self.execute_test(device_list=device_list, test_configuration=test_configuration,
                                           schedule_configuration=schedule_configuration,
                                           test_parameters=test_parameters, execution_type=execution_type,
                                           application_url=application_url,
                                           application_test_url=application_test_url)
        return status_message

    def test_now(self, client=None, device_list=None, test_configuration={}, test_parameters={},
                 application_url=None, application_test_url=None):
        schedule_configuration = {}
        # test_parameters = {
        #     "maxTestDuration": max_duration,
        #     "testFramework": test_framework,
        #     "projectName": project_name
        # }
        execution_type = "NOW"
        status_code, status_message = self.execute_test(device_list=device_list, test_configuration=test_configuration,
                                                        schedule_configuration=schedule_configuration,
                                                        test_parameters=test_parameters, execution_type=execution_type,
                                                        application_url=application_url,
                                                        application_test_url=application_test_url)
        return status_message

    def update_schedule(self, data=None, schedule_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        schedule_id = {
            "uuid": schedule_id
        }
        test_api_url = self.config.get("api_url") + "testexecute/edit/schedule"
        response = requests.put(test_api_url, json=data, params=schedule_id, headers=new_headers)
        print(response.json())

    def update_test(self, data=None, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        test_id = {
            "uuid": test_id
        }
        test_api_url = self.config.get("api_url") + "testexecute/edit/test"
        response = requests.put(test_api_url, json=data, params=test_id, headers=new_headers)
        print(response.json())
