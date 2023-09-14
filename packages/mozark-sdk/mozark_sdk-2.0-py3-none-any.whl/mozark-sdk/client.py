import configparser
from pathlib import Path

from mozark_sdk.user import User
from mozark_sdk.project import Project
from mozark_sdk.file import File
from mozark_sdk.device import Device
from mozark_sdk.tray import Tray
from mozark_sdk.executetest import TestExecute
from mozark_sdk.test_analytics import TestAnalytics


class Client:
    config = None

    def __init__(self):
        self.set_config()

    def set_config(self):
        config = configparser.ConfigParser()
        config_file = Path.home() / ".mozark" / "config"
        config.read(config_file)
        api_url = config.get("default", "MOZARK_APP_TESTING_URL")
        username = config.get("default", "MOZARK_APP_TESTING_USERNAME")
        password = config.get("default", "MOZARK_APP_TESTING_PASSWORD")
        client_id = config.get("default", "MOZARK_APP_TESTING_CLIENTID")
        base_download_dir = config.get("default", "BASE_DOWNLOAD_DIR")
        config = {"username": username, "password": password, "api_url": api_url, "client_id": client_id,
                  "base_download_dir": base_download_dir}
        self.config = config

    def get_config(self):
        return self.config

    def login(self):
        user = User(self)
        api_access_token = user.login()
        self.config["api_access_token"] = api_access_token

    def logout(self):
        self.config["api_access_token"] = ""

    # Project

    def create_project(self, project_name=None, project_description=None):
        """Create a new project
        Args:
            project_name (str): unique project name
            project_description (str): short description for a project

        Returns:
            message (str): 'Success' if successful, 'Failure' along with failure reason

            "Failure: Project with `{project_name}` already exists." - in case if project with the given name already exists
        """
        project = Project(self)
        status_message = project.create_project(project_name, project_description)
        return status_message

    def get_project_info(self, project_name=None):
        """ Returns project information -
        Args:
            project_name (str): project name

        Returns:
            project (dict): contains projectName, projectDescription, and unique ID
            {
                "projectName": "",
                "projectDescription": "",
                "projectUUID": ""
            }

            errorMessage (str): 'Failure: Project with name `{project_name}` not found.'
        """
        project = Project(self)
        status_message = project.get_project_info(project_name=project_name)
        return status_message

    def delete_project(self, project_name=None):
        """ Delete project with given project name

        Args:
            project_name (str): project name

        Returns:
            message (str): 'Success' if successful, 'Failure' along with failure reason
        """
        project = Project(self)
        status_message = project.delete_project(project_name=project_name)
        return status_message

    def get_project_list(self):
        """ Returns list of all projects

        Returns:
            projects (list): list of project dict

            [
                {
                    "projectName": "abc",
                    "projectDescription" : "abc desc",
                    "projectUUID": "aabbcc"
                },
                {
                    "projectName": "xyz",
                    "projectDescription": "xyz desc",
                    "projectUUID": "aabbcd"
                }
            ]

            errorMessage (str): "Failure: Project list is empty."

        """
        project = Project(client=self)
        status_message = project.get_project_list()
        return status_message

    # Application

    def upload_application(self, file_category=None, project_name=None, file_path=None):
        """ Upload android or ios application(.apk or .ipa) from given file path

        Args:
            file_category (str): Mandatory 'android-application' or 'ios-application'
            project_name (str): Container project for the application
            file_path (str): relative or absolute path of the file

        Returns:
            message (str): 'Success' if uploaded successfully, 'Failure' along with failure reason

            "Success: File `" + file_name + "` uploaded successfully."
            "Failure: File `" + file_name + "` not uploaded."
            "Error: File `" + file_name + "` already exists."
            "File Not Found Error: File `" + file_name + "` File not found or wrong path."

        """
        file = File(client=self)
        status = file.upload_application(file_category=file_category, project_name=project_name, file_path=file_path)
        return status

    def get_application_info(self, file_name=None):
        """ Returns file information

        Args:
            file_name (str): unique file name

        Returns:
            fileinfo (dict): dictionary containing the metadata about the file

            {
                "fileName" : "",
                "fileCategory": "android-application | ios-application",
                "md5": "",
                "fileURL": "",
                "fileUUID": "",
                "packageName": ""
            }

            errorMessage (str): "Failure: File with name `{file_name}` not found."

            Note:
                "packageName" is present in case of 'android-application'
        """
        file = File(client=self)
        app_list = file.get_application_info(file_name=file_name)
        return app_list

    def delete_application(self, file_name=None):
        """ Delete application with given file name
        Args:
            file_name (str): unique file name

        Returns:
            "Success: File `" + file_name + "` deleted successfully."
            "Failure: File `" + file_name + "` not deleted."
        """
        file = File(client=self)
        status = file.delete_file(file_name=file_name)
        return status

    def get_application_list(self, file_category=None, project_name=None):
        """ Returns list of all application file information

        Args:
            file_category (str): mandatory 'android-application' or 'ios-application'
            project_name (str): optional project_name to filter the android application files

        Returns:
            fileinfo (list): dictionary containing the metadata about the file

            [
                {
                    "fileName" : "",
                    "fileCategory": "android-application",
                    "md5": "",
                    "fileURL": "",
                    "fileUUID": "",
                    "packageName": "",
                    "projectName": ""
                },
                {
                    "fileName" : "",
                    "fileCategory": "ios-application",
                    "md5": "",
                    "fileURL": "",
                    "fileUUID": "",
                    "projectName": ""
                }
            ]

            Note: "projectName" will be present in response if passed in a filter, else the value will be ""
        """
        file = File(client=self)
        app_list = file.get_application_list(file_category=file_category, project_name=project_name)
        return app_list

    # Native Test Application

    def upload_native_test_application(self, file_category=None, project_name=None, file_path=None):
        """ Upload native test application(.apk or .ipa) from given file path

        Args:
            file_category (str): Mandatory 'android-application' or 'ios-application'
            project_name (str): Container project for the application
            file_path (str): relative or absolute path of the file

        Returns:
            message (str): 'Success' if uploaded successfully, 'Failure' along with failure reason

            "Success: File `" + file_name + "` uploaded successfully."
            "Failure: File `" + file_name + "` not uploaded."
            "Error: File `" + file_name + "` already exists."
        """
        file = File(client=self)
        status = file.upload_native_test_application(file_category=file_category,
                                                     project_name=project_name,
                                                     file_path=file_path)
        return status

    def get_native_test_application_info(self, file_name=None):
        """ Returns file information

        Args:
            file_name (str): unique file name

        Returns:
            fileinfo (dict): dictionary containing the metadata about the file

            {
                "fileName" : "",
                "fileCategory": "android-test-application | ios-test-application",
                "md5": "",
                "fileURL": "",
                "fileUUID": "",
                "testCodePackageName": "",
                "testRunnerName": "",
                "XCTestRunFileUrl": ""
            }

            errorMessage (str): "Failure: File with name `{file_name}` not found."

            Note:
                "testCodePackageName" and "testRunnerName" is present in case of 'android-test-application'
                "XCTestRunFileUrl" is present in case of 'ios-test-application'

        """
        file = File(client=self)
        app_list = file.get_native_test_application_info(file_name=file_name)
        return app_list

    def delete_native_test_application(self, file_name=None):
        """ Delete native test application with given file name
        Args:
            file_name (str): unique file name

        Returns:
            "Success: File `" + file_name + "` deleted successfully."
            "Failure: File `" + file_name + "` not deleted."
        """
        file = File(client=self)
        status = file.delete_file(file_name=file_name)
        return status

    def get_native_test_application_list(self, file_category=None, project_name=None):
        """ Returns list of all application file information

        Args:
            file_category (str): mandatory 'android-application' or 'ios-application'
            project_name (str): optional project_name to filter the android application files

        Returns:
            fileinfo (list): dictionary containing the metadata about the file

            [
                {
                    "fileName" : "",
                    "fileCategory": "android-test-application",
                    "md5": "",
                    "fileURL": "",
                    "fileUUID": "",
                    "testCodePackageName": "",
                    "testRunnerName": "",
                    "projectName": ""
                },
                {
                    "fileName" : "",
                    "fileCategory": "ios-test-application",
                    "md5": "",
                    "fileURL": "",
                    "fileUUID": "",
                    "XCTestRunFileUrl": ""
                    "projectName": ""
                }
            ]

            Note: "projectName" will be present in response if passed in a filter, else the value will be ""
        """
        file = File(client=self)
        app_list = file.get_native_test_application_list(file_category=file_category, project_name=project_name)
        return app_list

    # Device
    def add_device(self, device_parameter=None):
        """ Add Devices

                Args:
                    device_parameter(json): device details

                Returns:
                    message (str): 'Success'

                    "Failure: Device with name " + device_parameter["serial"] + " already exists."
                """
        device = Device(client=self)
        device_added = device.add_device(device_parameter=device_parameter)
        return device_added

    def get_device_list(self, platform=None, device_serial=None):
        """ Returns device information of all devices for a given platform or device_serial
        Args:
            platform (str): device platform type: 'android', 'ios', or 'living-room'
            device_serial (str): unique device serial

        Returns:
            device_info (list): list of dictionary containing the information about the device

            [
                {
                    "deviceSerial": "",
                    "deviceBrand": "",
                    "deviceCity": "",
                    "deviceCountry": "",
                    "deviceModelName": "",
                    "deviceModelNumber": "",
                    "devicePlatform": "android",
                    "deviceOSVersion": "",
                    "deviceSDKVersion": ["", ""],
                    "deviceUUID": "",
                    "deviceNetwork": ""
                },
                {
                    "deviceSerial": "",
                    "deviceBrand": "",
                    "deviceCity": "",
                    "deviceCountry": "",
                    "deviceModelName": "",
                    "deviceModelNumber": "",
                    "devicePlatform": "ios",
                    "deviceOSVersion": "",
                    "deviceSDKVersion": ["", ""],
                    "deviceUUID": "",
                    "deviceNetwork": ""
                },
                {
                    "deviceSerial": "",
                    "deviceBrand": "",
                    "deviceCity": "",
                    "deviceCountry": "",
                    "deviceModelName": "",
                    "deviceModelNumber": "",
                    "devicePlatform": "living-room",
                    "deviceOSVersion": "",
                    "deviceSDKVersion": ["", ""],
                    "deviceUUID": "",
                    "deviceNetwork": ""
                }
            ]
        """
        device = Device(client=self)
        device_list = device.get_devices(platform=platform, device_serial=device_serial)
        return device_list

    # def get_device_busy_slots(self, devices=None):
    #     pass

    def create_tray(self, platform=None, tray_name=None, device_list=None):
        """ Create tray for a given device platform category

        Args:
            platform(str): type of devices
            tray_name (str): Unique tray name(without spaces)
            device_list (list): device list

        Returns:
            message (str): 'Success' if tray is created successfully, 'Failure' along with failure reason

            "Failure: Tray with `{tray_name}` already exists." - in case if a tray with a given name already exists
        """
        tray = Tray(client=self)
        status = tray.create_tray(platform=platform, tray_name=tray_name, device_list=device_list)
        return status

    def get_tray_info(self, tray_name=None):
        """ Returns tray information for a given tray name
        Args:
            tray_name (str): Tray Name

        Returns:

            tray_info(dict): tray information along with device info

            {
                "trayName": "",
                "trayPlatform": "android",
                "trayUUID": "",
                "trayDevices" : [
                    {
                        "deviceSerial": "",
                        "deviceBrand": "",
                        "deviceCity": "",
                        "deviceCountry": "",
                        "deviceModelName": "",
                        "deviceModelNumber": "",
                        "devicePlatform": "android",
                        "deviceOSVersion": "",
                        "deviceSDKVersion": ["", ""],
                        "deviceUUID": "",
                        "deviceNetwork": ""
                    },
                    {
                        "deviceSerial": "",
                        "deviceBrand": "",
                        "deviceCity": "",
                        "deviceCountry": "",
                        "deviceModelName": "",
                        "deviceModelNumber": "",
                        "devicePlatform": "android",
                        "deviceOSVersion": "",
                        "deviceSDKVersion": ["", ""],
                        "deviceUUID": "",
                        "deviceNetwork": ""
                    }
                ]
            }
        """
        tray = Tray(client=self)
        tray_info = tray.get_tray_info(tray_name=tray_name)
        return tray_info

    def update_tray(self, tray_name=None, device_list=None):
        """ Update List of devices for a given tray name

        Args:
            tray_name(str): Tray name
            device_list(list): Updated device list

        Returns:
            message (str): 'Success' if tray is updated successfully, 'Failure' along with failure reason

            "Failure" in case of failure
        """
        tray = Tray(client=self)
        status = tray.update_tray(tray_name=tray_name, device_list=device_list)
        return status

    def delete_tray(self, tray_name=None):
        """ Delete tray with a given tray name

        Args:
            tray_name(str): Tray name

        Returns:
            message (str): 'Success' if tray is updated successfully, 'Failure' along with failure reason

            "Failure" in case of failure
        """
        tray = Tray(client=self)
        status = tray.delete_tray(tray_name=tray_name)
        return status

    def get_tray_list(self):
        """ Get tray list
        Returns:
            tray_list(list): List of tray info

            [
                {
                    "trayName": "",
                    "trayPlatform": "android",
                    "trayUUID": ""
                },
                {
                    "trayName": "",
                    "trayPlatform": "ios",
                    "trayUUID": ""
                },
                {
                    "trayName": "",
                    "trayPlatform": "living-room",
                    "trayUUID": ""
                }
            ]
        """
        tray = Tray(client=self)
        tray_list = tray.get_tray_list()
        return tray_list

    # Test Configuration & Test Parameters

    def get_supported_test_configuration(self, platform=None):
        mobile_test_configuration = {
            "captureHAR": False,
            "captureCPUMetrics": False,
            "captureMemoryMetrics": False,
            "captureBatteryMetrics": False,
            "captureGraphicsMetrics": False,
            "captureDeviceScreenShots": False,
            "recordDeviceScreen": False,
            "captureDeviceNetworkPackets": False
        }
        living_room_test_configuration = {
            "captureDeviceScreenShots": False,
            "recordDeviceScreen": False
        }
        config = {}
        if platform == "android":
            config = mobile_test_configuration
        elif platform == "ios":
            config = mobile_test_configuration
        elif platform == "living-room":
            config = living_room_test_configuration
        return config

    def get_default_test_parameters(self):
        test_parameters = {
            "maxTestDuration": 5,
            "testFramework": "android-uiautomator",
            "projectName": "",
        }
        return test_parameters

    def get_mandatory_test_parameters(self, platform=None):
        pass

    # Test Execution

    def start_test_execution(self,
                             project_name=None,
                             test_framework=None,
                             application_file_name=None,
                             test_application_file_name=None,
                             devices=None,
                             test_configuration=None,
                             test_parameters=None
                             ):
        """ Execute test now for a given configuration

        Args:
            project_name(str): project name
            test_framework(str): supported test framework 'android-uiautomator' or 'ios-xcuitest'
            application_file_name(str): file name of an application .apk or .ipa
            test_application_file_name: file name of a test application .apk or .ipa
            devices(list): list of device serial
            test_configuration(dict): test configuration as a key value pairs
            test_parameters(dict): test parameters as a key value pairs

        Returns:
            test_status(dict): test status containing the message and a test id to monitor

            {
                "message": "Success: Executed/Scheduled successfully",
                "testId": ""
            }
        """
        action = TestExecute(client=self)
        status = action.execute_test_now(project_name=project_name,
                                         test_framework=test_framework,
                                         application_file_name=application_file_name,
                                         test_application_file_name=test_application_file_name,
                                         devices=devices,
                                         test_configuration=test_configuration,
                                         test_parameters=test_parameters
                                         )
        return status

    def get_test_info(self, test_id=None):
        """ get test info

        Args:
            test_id(str):

        Returns:
            {
                "projectName" : "",
                "testFramework": "android-uiautomator | ios-xcuitest | living-room-automate",
                "applicationFileName": "",
                "testApplicationFileName": "",
                "device": "",
                "testStartTime": "",
                "testEndTime": "",
                "testUUID": "",
                "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                "testStatusDescription": ""
            }

        """
        action = TestExecute(client=self)
        status = action.get_test_info(test_id=test_id)
        return status

    def abort_test_execution(self, test_id=None):
        """ Abort a test which is running

        Args:
            test_id(str):

        Returns:
            testStatus(str): 'Success' if aborted successfully. 'Failure' with failure reason
        """
        action = TestExecute(client=self)
        status = action.abort_test(test_id=test_id)
        return status

    def schedule_test_execution(self,
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
        """ Execute test now for a given configuration

        Args:
            project_name(str): project name
            test_framework(str): supported test framework 'android-uiautomator' or 'ios-xcuitest'
            application_file_name(str): file name of an application .apk or .ipa
            test_application_file_name: file name of a test application .apk or .ipa
            devices(list): list of device serial
            test_configuration(dict): test configuration as a key value pairs
            test_parameters(dict): test parameters as a key value pairs
            start_date_time(datetime): schedule start date and time
            end_date_time(datetime): schedule end date and time
            interval(number): interval between two test runs

        Returns:
            test_status(dict): test status containing the message and a test id to monitor

            {
                "message": "Success: Executed/Scheduled successfully",
                "scheduleUUID": "",
                "testRuns": [
                    {
                        "testUUID" : "",
                        "testStartDateTime": "",
                    },
                    {
                        "testUUID" : "",
                        "testStartDateTime": "",
                    }
                ]
            }

        """
        action = TestExecute(client=self)
        status = action.schedule_test_executions(project_name=project_name,
                                                 test_framework=test_framework,
                                                 application_file_name=application_file_name,
                                                 test_application_file_name=test_application_file_name,
                                                 devices=devices,
                                                 test_configuration=test_configuration,
                                                 test_parameters=test_parameters,
                                                 start_date_time=start_date_time,
                                                 end_date_time=end_date_time,
                                                 interval=interval
                                                 )
        return status

    def update_schedule(self, data=None, schedule_id=None):
        action = TestExecute(client=self)
        """ Update schedule info

                Args:
                    schedule_id(str): schedule id
                    data(json): parameter

                Returns:
                    schedule_update (dict): Schedule Update Successfully
        """
        status = action.update_schedule(data=data, schedule_id=schedule_id)
        return status

    def update_test(self, data=None,test_id=None):
        action = TestExecute(client=self)
        """ Update test info

                Args:
                    test_id(str): test id
                    data(json): parameter
                    
                Returns:
                    test_update (dict): Test Update Successfully
        """
        status = action.update_test(data=data, test_id=test_id)
        return status

    def get_test_schedule_info(self, schedule_id=None):
        """ get test schedule info

        Args:
            schedule_id(str): schedule id

        Returns:
            schedule_info (dict): schedule information containing the list of test info

            {
                "scheduleUUID": "",
                "scheduleStartTime": "",
                "scheduleEndTime": "",
                "testInterval": "",
                "testConfiguration": {}
                "testParameters": {},
                "projectName" : "",
                "testFramework": "android-uiautomator | ios-xcuitest | living-room-automate",
                "applicationFileName": "",
                "testApplicationFileName": "",
                "testInfo": [
                    {
                        "device": "",
                        "testStartTime": "",
                        "testEndTime": "",
                        "testUUID": "",
                        "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                        "testStatusDescription": ""
                    },
                    {
                        "device": "",
                        "testStartTime": "",
                        "testEndTime": "",
                        "testUUID": "",
                        "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                        "testStatusDescription": ""
                    }
            }
        """
        action = TestExecute(client=self)
        status = action.get_test_schedule_info(schedule_id=schedule_id)
        return status

    def delete_test_schedule(self, schedule_id=None):
        """ Delete the test schedule

        Args:
            schedule_id(str):

        Returns:
            testScheduleStatus(str): 'Success' if deleted successfully. 'Failure' with failure reason
        """
        action = TestExecute(client=self)
        status = action.delete_schedule(schedule_id=schedule_id)
        return status

    def get_test_schedule_list(self, from_date_time=None, to_date_time=None):
        """ get list of test schedule info

        Returns:
            schedule_info(list): list of schedule info

            [
                {
                    "scheduleUUID": "",
                    "scheduleStartTime": "",
                    "scheduleEndTime": "",
                    "testInterval": "",
                    "testConfiguration": {}
                    "testParameters": {},
                    "projectName" : "",
                    "testFramework": "android-uiautomator | ios-xcuitest | living-room-automate",
                    "applicationFileName": "",
                    "testApplicationFileName": "",
                    "testInfo": [
                        {
                            "device": "",
                            "testStartTime": "",
                            "testEndTime": "",
                            "testUUID": "",
                            "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                            "testStatusDescription": ""
                        },
                        {
                            "device": "",
                            "testStartTime": "",
                            "testEndTime": "",
                            "testUUID": "",
                            "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                            "testStatusDescription": ""
                        }
                },
                {
                    "scheduleUUID": "",
                    "scheduleStartTime": "",
                    "scheduleEndTime": "",
                    "testInterval": "",
                    "testConfiguration": {}
                    "testParameters": {},
                    "projectName" : "",
                    "testFramework": "android-uiautomator | ios-xcuitest | living-room-automate",
                    "applicationFileName": "",
                    "testApplicationFileName": "",
                    "testInfo": [
                        {
                            "device": "",
                            "testStartTime": "",
                            "testEndTime": "",
                            "testUUID": "",
                            "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                            "testStatusDescription": ""
                        },
                        {
                            "device": "",
                            "testStartTime": "",
                            "testEndTime": "",
                            "testUUID": "",
                            "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                            "testStatusDescription": ""
                        }
                }
            ]
        """
        action = TestExecute(client=self)
        schedule_list = action.get_test_schedule_list(from_date_time=from_date_time, to_date_time=to_date_time)
        return schedule_list

    # Test Analytics
    def get_test_list(self, from_date_time=None, to_date_time=None):
        """ get list of test info

        Returns:
            test_info(list): list of test info

            [
                {
                    "projectName" : "",
                    "testFramework": "android-uiautomator | ios-xcuitest | living-room-automate",
                    "applicationFileName": "",
                    "testApplicationFileName": "",
                    "device": "",
                    "testStartTime": "",
                    "testEndTime": "",
                    "testUUID": "",
                    "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                    "testStatusDescription": ""
                },
                {
                    "projectName" : "",
                    "testFramework": "android-uiautomator | ios-xcuitest | living-room-automate",
                    "applicationFileName": "",
                    "testApplicationFileName": "",
                    "device": "",
                    "testStartTime": "",
                    "testEndTime": "",
                    "testUUID": "",
                    "testStatus": "SCHEDULED | STARTED | COMPLETED | ABORTED | FAILED",
                    "testStatusDescription": ""
                }
            ]
        """
        analytics = TestAnalytics(client=self)
        test_list = analytics.get_test_list(from_date_time=from_date_time, to_date_time=to_date_time)
        return test_list

    def get_test_execution_info_full(self, test_id=None):
        """ Get test execution info by test id

        Args:
            test_id: test id

        Returns:
            {
                "testUUID": "",
                "testStartDateTime": "",
                "testEndDateTime": "",
                "projectName": "",
                "applicationFileName": "",
                "testApplicationFileName": "",
                "deviceSerial": "",
                "deviceMake": "",
                "deviceModel": "",
                "deviceCity": "",
                "deviceCountry": "",
                "deviceNetwork": "",
                "devicePlatform": "",
                "deviceOSVersion": "",
                "deviceNetworkOperator": "",
                "testStatus": "",
                "testStatusDescription": "",
                "testCasesTotal": "",
                "testCasesPassed": "",
                "testCasesFailed": "",
                "testCases": [
                    {
                        "testCaseName": "",
                        "testCaseResult": "PASS | FAIL",
                        "testCaseStartDateTime": "",
                        "testCaseEndDateTime": "",
                    },
                    {
                        "testCaseName": "",
                        "testCaseResult": "PASS | FAIL",
                        "testCaseStartDateTime": "",
                        "testCaseEndDateTime": "",
                    },
                    {
                        "testCaseName": "",
                        "testCaseResult": "PASS | FAIL",
                        "testCaseStartDateTime": "",
                        "testCaseEndDateTime": "",
                    }
                ],
                "userExperienceKpis": [
                    {
                        "kpiName": "",
                        "kpiValue": "",
                        "testCaseName": ""
                    },
                    {
                        "kpiName": "",
                        "kpiValue": "",
                        "testCaseName": ""
                    },
                    {
                        "kpiName": "",
                        "kpiValue": "",
                        "testCaseName": ""
                    }
                ],
                "events": [
                    {
                        "eventName": "",
                        "eventDateTime": "",
                        "testCaseName": ""
                    },
                    {
                        "eventName": "",
                        "eventDateTime": "",
                        "testCaseName": ""
                    },
                    {
                        "eventName": "",
                        "eventDateTime": "",
                        "testCaseName": ""
                    }
                ]
            }
        """
        analytics = TestAnalytics(client=self)
        result = analytics.get_test_execution_info_full(test_id=test_id)
        return result

    def get_test_execution_info_by_section(self, test_id=None, section=None):
        """ Get Test Execution info by information section

        Args:
            test_id(str): test id
            section(str): supported info section names
                        - 'basic_test_info'
                        - 'test_configuration'
                        - 'test_cases'
                        - 'events'
                        - 'kpis_user_experience'
                        - 'kpis_api_performance_http'
                        - 'files_device_screenshots'
                        - 'files_device_screen_record'
                        - 'files_har'
                        - 'files_device_cpu_metrics'
                        - 'files_device_memory_metrics'
                        - 'files_device_battery_metrics'
                        - 'files_device_graphics_metrics'
                        - 'files_device_network_packets'
                        - 'files_device_debug_logs'
                        - 'files_test_execution_output'
                        - 'files_test_framework_output'
                        - 'kpis_system_performance_cpu_metrics'
                        - 'kpis_system_performance_memory_metrics'
                        - 'kpis_system_performance_battery_metrics'
                        - 'kpis_app_performance_graphics_metrics'
        Returns:
            section_info(dict): section information
        """
        analytics = TestAnalytics(client=self)
        response = analytics.get_test_execution_info_by_section(test_id=test_id, section=section)
        return response

    def download_by_section(self, test_id=None, section=None):
        """ Download test analytics information as a json file, raw file, list of raw files

        Args:
            test_id(str): test id
            section(str): supported info section names
                        - 'basic_test_info'                         - json
                        - 'test_configuration'                      - json
                        - 'test_cases'                              - json
                        - 'events'                                  - json
                        - 'kpis_user_experience'                    - json
                        - 'kpis_api_performance_http'               - json
                        - 'files_device_screenshots'                - png
                        - 'files_device_screen_record'              - mp4
                        - 'files_har'                               - har
                        - 'files_device_cpu_metrics'                - csv
                        - 'files_device_memory_metrics'             - csv
                        - 'files_device_battery_metrics'            - csv
                        - 'files_device_graphics_metrics'           - csv
                        - 'files_device_network_packets'            - pcap
                        - 'files_device_debug_logs'                 - log
                        - 'files_test_execution_output'             - log
                        - 'files_test_framework_output'             - log | xml | json | html
                        - 'kpis_system_performance_cpu_metrics'     - json
                        - 'kpis_system_performance_memory_metrics'  - json
                        - 'kpis_system_performance_battery_metrics' - json
                        - 'kpis_app_performance_graphics_metrics'   - json
        Returns:
            message(str) : 'Success: File filename downloaded successfully.'
                        : 'Failure: Error in downloading file filename.'
        """
        analytics = TestAnalytics(client=self)
        response = analytics.download_by_section(test_id=test_id, section=section)
        return response
