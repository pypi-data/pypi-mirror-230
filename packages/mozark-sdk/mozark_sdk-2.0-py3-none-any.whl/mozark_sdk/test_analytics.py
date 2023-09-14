import json
import requests
import os
from datetime import datetime


class TestAnalytics:
    config = None

    def __init__(self, client=None):
        self.config = client.get_config()

    def get_test_execution_info_full(self, test_id=None):

        test_info = self.get_test_information(test_id=test_id)
        kpi = self.get_test_kpis(test_id=test_id)
        events = self.get_test_events(test_id=test_id)
        testcases = self.get_test_testcases(test_id=test_id)

        test_information = {
            "test_info": test_info,
            "testCases": testcases,
            "userExperienceKpis": kpi,
            "events": events,
        }

        return test_information

    def is_datetime_in_range(self, start_datetime=None, end_datetime=None, check_datetime=None):
        # format = ['%Y-%m-%dT%H:%M%z', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S.%fZ']
        # format = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S']
        # if '+05:30' in check_datetime:
        #     check_datetime = check_datetime.split('+')
        #     check_datetime = datetime.strptime(check_datetime[0], format[0])
        # elif '+0530' in check_datetime:
        #     check_datetime = check_datetime.split('.')
        #     check_datetime = datetime.strptime(check_datetime[0], format[1])
        # else:
        #     check_datetime = check_datetime.split('.')
        #     check_datetime = datetime.strptime(check_datetime[0], format[2])
        check_datetime = check_datetime.split('T')
        if not check_datetime[0]:
            return False
        else:
            # print("\n :datetime ",check_datetime)
            check_datetime = datetime.strptime(check_datetime[0], '%Y-%m-%d')
            return start_datetime <= check_datetime <= end_datetime

    def get_test_list(self, from_date_time=None, to_date_time=None):
        test_info_list = []
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "analytics/tests"
        # Fetch list of tests
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            test_list = test_list['body']
            for i in range(len(test_list)):
                check_datetime = test_list[i]['testStartTime']
                # check=self.is_datetime_in_range(from_date_time, to_date_time, check_datetime)
                if self.is_datetime_in_range(from_date_time, to_date_time, check_datetime) == True:
                    # print(i, test_list[i])
                    if 'Scheduled' in test_list[i]['testStatus']:
                        testStatus = 'SCHEDULED'
                    elif 'Started' in test_list[i]['testStatus']:
                        testStatus = 'STARTED'
                    elif 'Completed' in test_list[i]['testStatus']:
                        testStatus = 'COMPLETED'
                    elif 'Aborted' in test_list[i]['testStatus']:
                        testStatus = 'ABORTED'
                    else:
                        testStatus = 'FAILED'

                    if '.ipa' in test_list[i]['scriptName']:
                        testFramework = "ios-xcuitest"
                    elif '.apk' in test_list[i]['scriptName']:
                        testFramework = "android-uiautomator"
                    else:
                        testFramework = "living-room-automate"

                    test_info = {
                        "projectName": test_list[i]['projectName'],
                        "testFramework": testFramework,
                        "applicationFileName": test_list[i]['appVersion'],
                        "testApplicationFileName": test_list[i]['scriptName'],
                        "device": test_list[i]['deviceName'],
                        "testStartTime": test_list[i]['testStartTime'],
                        "testEndTime": "",
                        "testUUID": test_list[i]['uuid']['testId'],
                        "testStatus": testStatus,
                        "testStatusDescription": test_list[i]['testStatus']
                    }
                    test_info_list.append(test_info)

            return test_info_list
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_information(self, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "analytics/tests/" + test_id + "/info"
        # Fetch info of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)

            try:
                test_info = test_list['body']
                print("\n test config: ", test_info)
                test_information = {
                    "testUUID": test_info['uuid']['testId'],
                    "testStartDateTime": test_info['testStartTime'],
                    "testEndDateTime": test_info['testEndTime'],
                    "projectName": test_info['projectName'],
                    "applicationFileName": test_info['appVersion'],
                    "testApplicationFileName": test_info['scriptName'],
                    "deviceSerial": test_info['deviceSerial'],
                    "deviceMake": "",
                    "deviceModel": test_info['deviceName'],
                    "deviceCity": test_info['deviceLocation'],
                    "deviceCountry": "",
                    "deviceNetwork": test_info['deviceNetwork'],
                    "devicePlatform": test_info['deviceOSVersion'],
                    "deviceOSVersion": test_info['deviceOSVersion'],
                    "deviceNetworkOperator": test_info['operator'],
                    "testStatus": test_info['testStatus'],
                    "testStatusDescription": test_info['testCaseSummary'],
                    "testCasesTotal": test_info['testCaseSummary']['total'],
                    "testCasesPassed": test_info['testCaseSummary']['passed'],
                    "testCasesFailed": test_info['testCaseSummary']['failed'],
                }

                return test_information
            except KeyError:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_configuration(self, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "analytics/tests/" + test_id + "/info"
        # Fetch info of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)

            try:
                testConfiguration = test_list['body']['testConfiguration']
                testConfig = {
                    'testConfiguration': testConfiguration
                }
                return testConfig
            except KeyError:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_testcases(self, test_id=None):
        testcaselist = []
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "analytics/tests/" + test_id + "/testcases"
        # Fetch info of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)

            try:
                testcases = test_list['body']
                for i in range(len(testcases['testCases'])):
                    testCaseName = testcases['testCases'][i]['testCaseName']
                    testCaseResult = testcases['testCases'][i]['status']
                    testCaseStartDateTime = ""
                    testCaseEndDateTime = ""

                    testcases_info = {
                        "testCaseName": testCaseName,
                        "testCaseResult": testCaseResult,
                        "testCaseStartDateTime": testCaseStartDateTime,
                        "testCaseEndDateTime": testCaseEndDateTime,
                    }
                    testcaselist.append(testcases_info)
                test_cases = {'test_cases': testcaselist}
                return test_cases
            except KeyError:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_events(self, test_id=None):
        eventexp = []
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "analytics/tests/" + test_id + "/app/events"
        # Fetch events of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            try:
                events = test_list['body']
                for i in range(len(events["events"])):
                    eventname = events["events"][i]['eventName']
                    eventdatetime = events["events"][i]['time']
                    testcasename = events["events"][i]['testCase']

                    event_info = {
                        "eventName": eventname,
                        "eventDateTime": eventdatetime,
                        "testCaseName": testcasename
                    }
                    eventexp.append(event_info)
                events = {'events': eventexp}
                return events
            except KeyError:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_kpis(self, test_id=None):
        userexperiancekpi = []

        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "analytics/tests/" + test_id + "/app/kpi/experience"
        # Fetch kpis of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            try:
                kpi = test_list['body']
                for i in range(len(kpi["experience"])):
                    kpiname = kpi["experience"][i]['kpiName']
                    kpivalue = kpi["experience"][i]['value']
                    testcasename = ""

                    kpi_info = {"kpiName": kpiname,
                                "kpiValue": kpivalue,
                                "testCaseName": testcasename
                                }
                    userexperiancekpi.append(kpi_info)
                kpis_user_experience = {'kpis_user_experience': userexperiancekpi}
                return kpis_user_experience
            except KeyError:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_apis(self, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
        }
        test_api_url = self.config.get("api_url") + "analytics/tests/" + test_id + "/app/resource/httpapi"
        # Fetch http apis of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            try:
                test_list = test_list['body']
                return test_list
            except:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def get_test_screenshot_list(self, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
            "testId": test_id,
            "type": "screenshots"
        }
        test_api_url = self.config.get("api_url") + "testexecute/download"
        # Fetch screenshots of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            try:
                test_list = test_list['data']['list']
            except KeyError:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
            return test_list
        else:
            return None

    def get_test_output_file_list(self, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
            "testId": test_id,
            "type": "output"
        }
        test_api_url = self.config.get("api_url") + "testexecute/download"
        # Fetch screenshots of test
        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            try:
                test_list = test_list['data']['list']
            except KeyError:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
            return test_list
        else:
            return {"statusCode:": response.status_code, "message": response.text}

    def download_test_screenshot(self, test_id=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        test_api_url = self.config.get("api_url") + "testexecute/download"
        make_test_id_dir = self.config.get("base_download_dir") + test_id
        if not os.path.exists(make_test_id_dir):
            os.mkdir(make_test_id_dir)
        output_path = make_test_id_dir
        list_screenshots = self.get_test_screenshot_list(test_id=test_id)
        if list_screenshots:
            for i in range(len(list_screenshots)):
                file_name = list_screenshots[i]
                new_params = {
                    "testId": test_id,
                    "type": "screenshots",
                    "fileName": file_name
                }

                # Fetch screenshots of test
                response = requests.get(test_api_url, params=new_params, headers=new_headers)
                if response.status_code == 200:
                    test_list = json.loads(response.text)
                    try:
                        test_list = test_list['data']['list']
                        new_response = requests.get(test_list['url'])
                        file_name = os.path.join(output_path, file_name)
                        open(file_name, "wb").write(new_response.content)
                    except:
                        return {"statusCode:": response.status_code,
                                "message": f'Nothing in body for test_id {test_id}'}
            return f'Success: File downloaded successfully.'
        else:
            return f'Failure: Error in downloading file.'

    def download_test_output_file(self, test_id=None, file_name=None):
        make_test_id_dir = self.config.get("base_download_dir") + test_id
        if not os.path.exists(make_test_id_dir):
            os.mkdir(make_test_id_dir)
        output_path = make_test_id_dir

        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
            "testId": test_id,
            "type": "output",
            "fileName": file_name
        }

        test_api_url = self.config.get("api_url") + "testexecute/download"

        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            try:
                test_list = test_list['data']['list']

                new_response = requests.get(requests.utils.unquote(test_list['url']))

                file_name = os.path.join(output_path, file_name)
                open(file_name, "wb").write(new_response.content)
                return f'Success: File downloaded successfully.'
            except:
                return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
        else:
            return f'Failure: Error in downloading file.'

    def download_by_section(self, test_id=None, section=None):

        if section == 'basic_test_info':
            make_json = self.get_test_information(test_id=test_id)
            response = self.create_json(test_id=test_id, section=section, make_json=make_json)

        elif section == 'test_configuration':
            make_json = self.get_test_configuration(test_id=test_id)
            response = self.create_json(test_id=test_id, section=section, make_json=make_json)
        elif section == 'test_cases':
            make_json = self.get_test_testcases(test_id=test_id)
            response = self.create_json(test_id=test_id, section=section, make_json=make_json)

        elif section == 'events':
            make_json = self.get_test_events(test_id=test_id)
            response = self.create_json(test_id=test_id, section=section, make_json=make_json)

        elif section == 'kpis_user_experience':
            make_json = self.get_test_kpis(test_id=test_id)
            response = self.create_json(test_id=test_id, section=section, make_json=make_json)

        # need to handle error if body not present
        elif section == 'kpis_api_performance_http':
            make_json = self.get_test_apis(test_id=test_id)
            print(make_json)
            response = self.create_json(test_id=test_id, section=section, make_json=make_json)

        elif section == 'files_device_screenshots':
            response = self.download_test_screenshot(test_id=test_id)

        elif section == 'kpis_system_performance_cpu_metrics':
            pass
        elif section == 'kpis_system_performance_memory_metrics':
            pass
        elif section == 'kpis_system_performance_battery_metrics':
            pass
        elif section == 'kpis_app_performance_graphics_metrics':
            pass

        else:
            file_lists = self.get_test_output_file_list(test_id=test_id)
            # print("\n file lists: ", file_lists)
            if section == 'files_device_screen_record':
                if 'final_video.mp4' in file_lists:
                    file_name = 'final_video.mp4'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_har':
                if 'har_logs.har' in file_lists:
                    file_name = 'har_logs.har'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_cpu_metrics':
                if 'cpu.txt' in file_lists:
                    file_name = 'cpu.txt'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_memory_metrics':
                if 'memory.txt' in file_lists:
                    file_name = 'memory.txt'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_battery_metrics':
                if 'battery.txt' in file_lists:
                    file_name = 'battery.txt'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_graphics_metrics':
                if 'frames.txt' in file_lists:
                    file_name = 'frames.txt'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_network_packets':
                if 'packet.pcap' in file_lists:
                    file_name = 'packet.pcap'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_debug_logs':
                if 'systemDebugLogs.log' in file_lists:
                    file_name = 'systemDebugLogs.log'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_test_execution_output':
                if 'execution.log' in file_lists:
                    file_name = 'execution.log'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'

            # this file not available need error handle
            elif section == 'files_test_framework_output':
                if 'framework.log' in file_lists:
                    file_name = 'framework.log'
                    response = self.download_test_output_file(test_id=test_id, file_name=file_name)
                else:
                    response = f'Failure: Error in downloading file.'
            else:
                response = f'Failure: Error in downloading file.'
        return response

    def get_info_url_for_file(self, test_id=None, file_name=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        new_params = {
            "testId": test_id,
            "type": "output",
            "fileName": file_name
        }

        test_api_url = self.config.get("api_url") + "testexecute/download"

        response = requests.get(test_api_url, params=new_params, headers=new_headers)
        if response.status_code == 200:
            test_list = json.loads(response.text)
            test_list = test_list['data']['list']
            return test_list['url']

    def get_info_url_for_screenshot(self, test_id=None):
        url_list = []
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        test_api_url = self.config.get("api_url") + "testexecute/download"

        list_screenshots = self.get_test_screenshot_list(test_id=test_id)
        if list_screenshots:
            for i in range(len(list_screenshots)):
                file_name = list_screenshots[i]
                new_params = {
                    "testId": test_id,
                    "type": "screenshots",
                    "fileName": file_name
                }

                # Fetch screenshots of test
                response = requests.get(test_api_url, params=new_params, headers=new_headers)
                if response.status_code == 200:
                    test_list = json.loads(response.text)
                    try:
                        test_list = test_list['data']['list']
                        url_list.append(test_list['url'])
                    except KeyError:
                        return {"statusCode:": response.status_code, "message": f'Nothing in body for test_id {test_id}'}
            return url_list
        else:
            return f'Failure: Error in information.'

    def get_test_execution_info_by_section(self, test_id=None, section=None):
        if section == 'basic_test_info':
            response = self.get_test_information(test_id=test_id)
        elif section == 'test_configuration':
            response = self.get_test_configuration(test_id=test_id)
        elif section == 'test_cases':
            response = self.get_test_testcases(test_id=test_id)

        elif section == 'events':
            response = self.get_test_events(test_id=test_id)

        elif section == 'kpis_user_experience':
            response = self.get_test_kpis(test_id=test_id)

        # need to handle error if body not present
        elif section == 'kpis_api_performance_http':
            response = self.get_test_apis(test_id=test_id)

        elif section == 'files_device_screenshots':
            response = self.get_info_url_for_screenshot(test_id=test_id)
            response = {"fileURL": response}

        elif section == 'kpis_system_performance_cpu_metrics':
            pass
        elif section == 'kpis_system_performance_memory_metrics':
            pass
        elif section == 'kpis_system_performance_battery_metrics':
            pass
        elif section == 'kpis_app_performance_graphics_metrics':
            pass

        else:
            file_lists = self.get_test_output_file_list(test_id=test_id)
            # print("\n file lists: ", file_lists)
            if section == 'files_device_screen_record':
                if 'final_video.mp4' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='final_video.mp4')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_har':
                if 'har_logs.har' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='har_logs.har')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_cpu_metrics':
                if 'cpu.txt' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='cpu.txt')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_memory_metrics':
                if 'memory.txt' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='memory.txt')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_battery_metrics':
                if 'battery.txt' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='battery.txt')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_graphics_metrics':
                if 'frames.txt' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='frames.txt')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_network_packets':
                if 'packet.pcap' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='packet.pcap')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_device_debug_logs':
                if 'systemDebugLogs.log' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='systemDebugLogs.log')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            elif section == 'files_test_execution_output':
                if 'execution.log' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='execution.log')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'

            # this file not available need error handle
            elif section == 'files_test_framework_output':
                if 'framework.log' in file_lists:
                    response = self.get_info_url_for_file(test_id=test_id, file_name='framework.log')
                    response = {"fileURL": response}
                else:
                    response = f'Failure: Error in downloading file.'
            else:
                response = f'Failure: Error in downloading file.'
        return response

    def create_json(self, test_id=None, section=None, make_json=None):
        if "statusCode:" not in make_json:
            file_name = self.write_to_file(test_id=test_id, section=section, make_json=make_json)
            response = f'Success: File {file_name} downloaded successfully.'
        else:
            response = f'Failure: Error in downloading file.'
        return response

    def write_to_file(self, test_id=None, section=None, make_json=None):
        make_test_id_dir = self.config.get("base_download_dir") + test_id
        if not os.path.exists(make_test_id_dir):
            os.mkdir(make_test_id_dir)
        output_path = make_test_id_dir
        file_name = f'{output_path}/{section}.json'
        with open(file_name, "w") as outfile:
            outfile.write(json.dumps(make_json))
        return file_name
