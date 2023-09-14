import json
from pathlib import Path

import requests


class Device:
    config = None

    def __init__(self, client=None):
        self.config = client.get_config()

    def add_device(self, device_parameter=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}

        if device_parameter["platform"] == "living-room":
            device_parameter["platform"] = "TV"
        # print(device_parameter)
        device_api_url = self.config.get("api_url") + "testexecute/devices"
        response = requests.post(device_api_url, json=device_parameter, headers=new_headers)
        print(response.json())
        try:
            if response.json()["status"] == 200 and response.json()["message"] == "Success":
                return "Success"
            else:
                return "Failure: Device with name " + device_parameter["serial"] + " already exists."
        except KeyError:
            return "Failure: Device with name " + device_parameter["serial"] + " already exists."

    def get_devices(self, platform=None, device_serial=None):
        new_headers = {'Authorization': "Bearer " + self.config.get("api_access_token"),
                       'Content-Type': 'application/json'}
        if platform == "living-room":
            platform = "TV"
        new_params = {
            "platform": platform,
            "serial": device_serial
        }
        device_api_url = self.config.get("api_url") + "testexecute/devices"
        # Fetch list of devices
        response = requests.get(device_api_url, params=new_params, headers=new_headers)

        device_list = response.json()['data']['list']
        return_message = []
        if len(device_list) > 0:
            for d in device_list:
                if d['platform'] == "TV":
                    device_platform = "living-room"
                else:
                    device_platform = d['platform']
                if device_platform == 'android':
                    file_info = {"deviceSerial": d['serial'],
                                 "deviceBrand": d['brand'],
                                 "deviceCity": d['deviceParameters']['city'],
                                 "deviceCountry": d['deviceParameters']['country'],
                                 "deviceModelName": d['modelName'],
                                 "deviceModelNumber": d['modelNumber'],
                                 "devicePlatform": d['platform'],
                                 "deviceOSVersion": d['osVersion'],
                                 "deviceSDKVersion": d['sdkVersion'],
                                 "deviceUUID": d['uuid'],
                                 "deviceNetwork": d['deviceParameters']['network']
                                 }
                    return_message.append(file_info)
                elif device_platform == 'ios':
                    file_info = {"deviceSerial": d['serial'],
                                 "deviceBrand": d['brand'],
                                 "deviceCity": d['deviceParameters']['city'],
                                 "deviceCountry": d['deviceParameters']['country'],
                                 "deviceModelName": d['modelName'],
                                 "deviceModelNumber": d['modelNumber'],
                                 "devicePlatform": d['platform'],
                                 "deviceOSVersion": d['osVersion'],
                                 "deviceSDKVersion": d['sdkVersion'],
                                 "deviceUUID": d['uuid'],
                                 "deviceNetwork": d['deviceParameters']['network']
                                 }
                    return_message.append(file_info)
                elif device_platform == 'living-room':
                    file_info = {"deviceSerial": d['serial'],
                                 "deviceBrand": d['brand'],
                                 "deviceCity": d['deviceParameters']['city'],
                                 "deviceCountry": d['deviceParameters']['country'],
                                 "deviceModelName": d['modelName'],
                                 "deviceModelNumber": d['modelNumber'],
                                 "devicePlatform": device_platform,
                                 "deviceOSVersion": d['osVersion'],
                                 "deviceSDKVersion": d['sdkVersion'],
                                 "deviceUUID": d['uuid'],
                                 "deviceNetwork": d['deviceParameters']['network']
                                 }
                    return_message.append(file_info)
        return return_message
