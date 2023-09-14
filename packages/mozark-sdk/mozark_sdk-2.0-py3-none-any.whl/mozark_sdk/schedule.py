
class Schedule:
    devices = None
    test_configuration = {
        "captureHAR": False,
        "captureCPUMetrics": False,
        "captureMemoryMetrics": False,
        "captureBatteryMetrics": False,
        "captureGraphicsMetrics": False,
        "captureDeviceScreenShots": False,
        "recordDeviceScreen": False,
        "captureDeviceNetworkPackets": False,
        "captureAutomationLogs": False,
        "captureSystemDebugLogs": False,
        "captureLiveLogs": False
    }
    schedule_configuration = {}
    test_action = {}
    test_parameters = {}
    application_url = None
    test_application_url = None
    executionType = "NOW"

    def __init__(self):
        pass

    def set_test_configuration(self, test_configuration = None):
        pass




