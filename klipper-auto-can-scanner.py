import sys
import time
import json
import configparser
import subprocess
import logging

VERSION = "0.1b-20250119"
CONFIG_FILE = "./config.json"
LOG_FILE = "klipper-auto-can-scanner.log"
LOG_LEVEL = logging.INFO
SERVICE_CONFIG = None
KLIPPER_CONFIG = None

logging.basicConfig(level=LOG_LEVEL,  handlers=[logging.FileHandler(LOG_FILE, mode='w'), logging.StreamHandler()], format="%(asctime)-15s %(levelname)-8s %(message)s")


def getCanDeviceUUID(venvPath,scannerPath,canBus,blackList,whiteList):
    # ~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
    # Found canbus_uuid=11aa22bb33cc, Application: Klipper
    command = [venvPath, scannerPath, canBus]
    deviceUUID = None

    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True,
            text=True,
            capture_output=True
        )
        print("Output:")
        print(result.stdout)
        return True, deviceUUID
    except subprocess.CalledProcessError as e:
        print("Error:")
        print(e.stderr)
        return False, deviceUUID

def writeKlipperConfig(canDeviceUUID):
    return False


class SystemConfig(object):

    def __init__(self, configFile):
        self.configOk = True
        configJson = {}
        with open(configFile) as config_file:
            configJson = json.loads(config_file.read())
        # check params
        if "variablesFile" not in configJson or "moonrakerPort" not in configJson or "updateInterval" not in configJson or "taskList" not in configJson or "apiTimeout" not in configJson:
            raise ValueError("Missing parameter(s)")
        if type(configJson["variablesFile"]) != str or configJson["variablesFile"] == "":
            raise ValueError("Invalid moonrakerPort")
        if type(configJson["moonrakerPort"]) != int or configJson["moonrakerPort"] <= 0:
            raise ValueError("Invalid moonrakerPort")
        if type(configJson["apiTimeout"]) != int or configJson["apiTimeout"] <= 0:
            raise ValueError("Invalid apiTimeout")
        if type(configJson["updateInterval"]) != int or configJson["updateInterval"] <= 0:
            raise ValueError("Invalid updateInterval")
        if type(configJson["taskList"]) != list or len(configJson["taskList"]) <= 0:
            raise ValueError("Invalid taskList")

        self.variablesFile = configJson["variablesFile"]
        self.moonrakerPort = configJson["moonrakerPort"]
        self.apiTimeout = configJson["apiTimeout"]
        self.updateInterval = configJson["updateInterval"]
        self.taskList = []

        for rawTask in configJson["taskList"]:
            tmpTask = Task(rawTask)
            self.taskList.append(tmpTask)



def readConfig(configFile):
    return False,None



def readKlipperConfig(configFile):
    return False, None

def restartKlipper():
    try:
        # Restart the service
        subprocess.run(["systemctl", "restart", "klipper"], check=True)
        logging.info("Klipper restarted successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error("Failed to restart klipper. Error : " + str(e))
        return False


def main():
    success, SERVICE_CONFIG = readConfig(CONFIG_FILE)
    if not success:
        logging.error("Cannot read service config file : " + CONFIG_FILE)
        sys.exit(1)

    success, KLIPPER_CONFIG = readKlipperConfig(SERVICE_CONFIG["klipperConfigFile"])
    if not success:
        logging.error("Cannot read klipper config file : " + SERVICE_CONFIG["klipperConfigFile"])
        sys.exit(1)

    if SERVICE_CONFIG["deviceConfigName"] not in KLIPPER_CONFIG:
        logging.error("CAN device config " + SERVICE_CONFIG["deviceConfigName"] + "not found in klipper config")
        sys.exit(1)

    success, deviceUUID = getCanDeviceUUID(SERVICE_CONFIG["klipperVenvPath"], SERVICE_CONFIG["scannerPath"], SERVICE_CONFIG["canBus"], SERVICE_CONFIG["blackList"], SERVICE_CONFIG["whiteList"])
    if not success:
        logging.error("CAN device UUID not found")
        sys.exit(1)
    logging.info("Found device " + deviceUUID)

    # check if saved UUID is the same as scanned one

    logging.info("Overwrite klipper config file with new CAN UUID")
    success = writeKlipperConfig(deviceUUID)
    if not success:
        logging.error("Cannot overwrite klipper config file : " + SERVICE_CONFIG["klipperConfigFile"])
        sys.exit(1)

    if SERVICE_CONFIG["restartKlipper"]:
        success = restartKlipper()
        if not success:
            logging.error("Cannot restart klipper service")
        sys.exit(1)

    logging.info("Updated CAN device UUID :" + deviceUUID)
    return 0


if __name__ == "__main__":
    main()
