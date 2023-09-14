# MOZARK Python SDK

The MOZARK Python SDK makes it easier to integrate test execution workflows on MOZARK device platform.

This Python SDK implements Client interface to access various MOZARK application testing features. It abstracts the HTTP API implementation and provides a simpler interface to read and manipulate various feature domain objects.

> See our [changelog](./CHANGELOG.md).

Table of contents
=================

* [Features](#features)
* [Releases](#releases)
* [Installation](#installation)
  * [Requirements](#requirements)
  * [Configuration](#configuration)
* [Getting Started](#getting-started)
  * [Integration](#integration)
  * [Quickstart](#quickstart)
  * [Examples](#examples)

## Features

**User Authentication**: All the subsequence features are access controlled using the `api_access_token` generated as an output of `login()` workflow. User need to configure credentials and API URL in the `config` file as per instructions detailed in this documentation.  

**Projects**: User can use projects to organize application builds, test application code, test results etc.

**Application Builds**: User can upload different versions build files(`.apk` or `.ipa`) of the application under testing.

**Test Application Builds**: User can upload different versions test automation files(`.apk` or `.ipa`).

**Device Selection**: From the set of android, ios, and living room devices; user can select one or many devices to execute the user scenarios to test application under test.

**Device Trays**: Device trays enables user to save the selection of devices which are used frequently. 

**Executing Tests**: During the development of test code for required user scenarios user can execute a test to do a quick sanity check.

**Scheduling Periodic Tests**: In order to capture test outcomes at different time of the day, user can choose to schedule execution of test code on selected set of devices.

**Checking Test Execution Results**: The outcome of each of the test execution on device(sanity check or scheduled run) can be checked independently. The test execution results include basic test status information, individual test case status, events captured during the automated user scenario, KPIs calculated from the events captured, and various other artifacts captured during the test execution. 

**Recommended usage**: Users are recommended to make use of scheduling test execution, which offer simpler control to cancel set of expected test runs in case of test failures.

## Releases
* The [changelog](CHANGELOG.md) provides a summary of changes in each release.

## Installation

### Requirements

* Python 3.0 and above
* pip for installing python dependencies

### Configuration

Add `mozark-sdk` to your `requirements.txt` dependencies. You may also use pip command to install `mozark-sdk` into your Python virtual environment.
```commandline
pip install mozark-sdk
```

## Getting Started

### Integration

Get started with our [📚 integration guides](DOCUMENTATION.md#scheduling-tests) or check SDK reference:
```python
from mozark_sdk.client import Client

client = Client()
help(client)
```

### Quickstart

Configure API URL, user credentials, and client ID.

Create a configuration file with a name `config` under `.mozark` directory within your home folder. The template of the configuration file is as below:

```
[default]
MOZARK_APP_TESTING_URL={url}
MOZARK_APP_TESTING_USERNAME={username}
MOZARK_APP_TESTING_PASSWORD={password}
MOZARK_APP_TESTING_CLIENTID={client_id}
BASE_DOWNLOAD_DIR={local_download_base_dir}
```

The `login()` api reads the information mentioned in `$HOME/.mozark/config` and sets the `api_access_token` to be further used in subsequent APIs.

To get a list of projects created on MOZARK application testing platform:
```python
from mozark_sdk.client import Client

client = Client()

client.login()

project_list = client.get_project_list()
```
 
### Examples

**Create a project**

```python
from mozark_sdk.client import Client

client = Client()

client.login()

project_name = "Android App Performance Testing"
project_description = "This project evaluate the quality of application experience in real user scenarios"

project_list = client.create_project(project_name=project_name, project_description=project_description)
```

**Upload an application build package**

```python
from mozark_sdk.client import Client

client = Client()

client.login()

project_name = "Android App Performance Testing"
file_path = "./MyApplication-1.0.apk"
file_category = 'android-application'

message = client.upload_application(file_category=file_category,
                                    project_name=project_name,
                                    file_path=file_path)
```

**Upload a native test application build package**

```python
from mozark_sdk.client import Client

client = Client()

client.login()

project_name = "Android App Performance Testing"
file_path = "./my-experience-test-1.0.apk"
file_category = 'android-test-application'

project_list = client.upload_native_test_application(file_category=file_category,
                                                     project_name=project_name,
                                                     file_path=file_path)
```

**Get a list of devices**

```python
from mozark_sdk.client import Client

client = Client()

client.login()

project_name = "Android App Performance Testing"
file_path = "./my-experience-test-1.0.apk"
file_category = 'android-test-application'

device_list = client.get_device_list(platform="android")

device_serial_list = []
for device in device_list:
  device_serial_list.append(device["deviceSerial"])
```

**Execute a test**

```python
from mozark_sdk.client import Client

client = Client()

client.login()

project_name = "Android App Performance Testing"
test_framework = "android-uiautomator"
application_file_name = "my-experience-test-1.0.apk"
test_application_file_name = "my-experience-test-1.0.apk"
device_list = client.get_device_list(platform="android")

# Get a list of device serial numbers

device_serial_list = []
for device in device_list:
  device_serial_list.append(device["deviceSerial"])

# Configure test run to capture device screenshots, record device screen, capture test code automation console logs, device logs etc.

test_configuration = {
  "captureDeviceScreenShots": True,
  "recordDeviceScreen": True,
  "captureAutomationLogs": True,
  "captureSystemDebugLogs": True
}

# Set a maximum test duration of 10 minutes, after 10 minutes the test should abort. 
test_parameters = {
  "maxTestDuration": 10
}

test_run = client.start_test_execution(project_name=project_name,
                                       test_framework=test_framework,
                                       application_file_name=application_file_name,
                                       test_application_file_name=test_application_file_name,
                                       devices=device_serial_list,
                                       test_configuration=test_configuration,
                                       test_parameters=test_parameters)

       
test_id = test_run["testId"]
print(test_id)
```

**Analyze test execution outcomes**

```python
from mozark_sdk.client import Client

client = Client()

client.login()

test_list = client.get_test_list()

test_id = test_list[0]["testUUID"]
test_info = client.get_test_execution_info_full(test_id=test_id)

# Get a list of test cases and their status
test_case_status = test_info["testCases"]
```
