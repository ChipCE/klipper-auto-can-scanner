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


logging.basicConfig(level=LOG_LEVEL,  handlers=[logging.FileHandler(LOG_FILE, mode='w'), logging.StreamHandler()], format="%(asctime)-15s %(levelname)-8s %(message)s")


def getCanDeviceUUIDs(scannerPath,timeout):
    deviceUUIDs = []
    try:
        result = subprocess.run(['bash', scannerPath], capture_output=True, text=True, timeout = timeout)

        # Check the output
        logging.info("ReturnCode : " + str(result.returncode))
        logging.info("Stdout : " + str(result.stdout))
        logging.info("Stderr : " + str(result.stderr))

        lines = result.stdout.split("\n")
        logging.info("stdout line count : " + str(len(lines)))
        if len(lines) == 0:
            logging.info("No UUID found")
            return True, deviceUUIDs
        
        for line in lines:
            if "Found canbus_uuid=" in line and "Application: Klipper" in line:
                segments = line.split(" ")
                for segment in segments:
                    if "canbus_uuid=" in segment:
                        uuid = segment.replace("canbus_uuid=","").replace(",","")
                        logging.info("Found " + uuid + " in stdout.")
                        deviceUUIDs.append(uuid)
        logging.info("Found " + str(len(deviceUUIDs)) + " UUID(s).")
        return len(deviceUUIDs) > 0,deviceUUIDs
    except Exception as e:
        logging.error("Get CAN device UUIDs error : " + str(e))
        return False, []

def readServiceConfig(configFile):
    try:
        with open(configFile) as serviceConfig:
            serviceConfigJson = json.loads(serviceConfig.read())
            hasError = False

            if type(serviceConfigJson["klipperConfigFile"]) != str or serviceConfigJson["klipperConfigFile"] == "":
                logging.error("Invalid config : klipperConfigFile")
                hasError = True

            if type(serviceConfigJson["scannerPath"]) != str or serviceConfigJson["scannerPath"] == "":
                logging.error("Invalid config : scannerPath")
                hasError = True
        
            if type(serviceConfigJson["scanTimeout"]) != int:
                logging.error("Invalid config : scanTimeout")
                hasError = True

            if type(serviceConfigJson["restartKlipper"]) != bool:
                logging.error("Invalid config : restartKlipper")
                hasError = True

            if type(serviceConfigJson["deviceConfigName"]) != str or serviceConfigJson["deviceConfigName"] == "":
                logging.error("Invalid config : deviceConfigName")
                hasError = True

            if type(serviceConfigJson["blackList"]) != list:
                logging.error("Invalid config : ")
                hasError = True

            if type(serviceConfigJson["whiteList"]) != list:
                logging.error("Invalid config : ")
                hasError = True

            return not hasError,serviceConfigJson
    except Exception as e:
        logging.error("Failed to read service config : " + str(e))
        return False,None
    return False,None

def readKlipperConfig(configFile):
    try:
        config = configparser.ConfigParser(delimiters=(':','='))
        config.read(configFile)
        if len(config.sections()) == 0:
            return False, None
        return True, config
    except Exception as e:
        logging.error("Failed to read klipper config : " + str(e))
        return False, None
    return False, None

def getSavedConfig(configFile):
    savedConfig = []
    try:
        with open(configFile) as configfile:
            lines = configfile.readlines()
            foundSavedConfig = False
            for line in lines:
                if line == "#*# <---------------------- SAVE_CONFIG ---------------------->\n":
                    foundSavedConfig = True
                if foundSavedConfig:
                    savedConfig.append(line)
    except Exception as e:
        logging.warning("Failed to read saved config : " + str(e))
        return False,[]
    return True,savedConfig

def writeKlipperConfig(klipperConfig,savedConfig,configFile):
    with open(configFile, "w") as printerCfg:
        try:
            klipperConfig.write(printerCfg)
        except Exception as e:
            logging.error("Failed to write klipper config : " + str(e))
            return False
        
        try:
            if len(savedConfig) > 0:
                printerCfg.writelines(savedConfig)
        except Exception as e:
            logging.error("Failed to write saved config : " + str(e))
            return False
    return True

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
    SERVICE_CONFIG = None
    KLIPPER_CONFIG = None
    SAVED_CONFIG = []
    MAIN_MCU_UUID = ""
    CURRENT_TOOLHEAD_UUID = ""

    # read service config
    success, SERVICE_CONFIG = readServiceConfig(CONFIG_FILE)
    if not success:
        logging.error("Cannot read service config file : " + CONFIG_FILE)
        sys.exit(1)

    # read current configs
    success, KLIPPER_CONFIG = readKlipperConfig(SERVICE_CONFIG["klipperConfigFile"])
    if not success:
        logging.error("Cannot read klipper config file : " + SERVICE_CONFIG["klipperConfigFile"])
        sys.exit(1)
    success, SAVED_CONFIG = getSavedConfig(SERVICE_CONFIG["klipperConfigFile"])
    if not success:
        logging.error("Cannot read saved config file : " + SERVICE_CONFIG["klipperConfigFile"])
        sys.exit(1)

    # current config content check
    if not KLIPPER_CONFIG.has_option("mcu","canbus_uuid"):
        logging.error("Invalid klipper config : [mcu]")
        sys.exit(1)
    else:
        MAIN_MCU_UUID = KLIPPER_CONFIG["mcu"]["canbus_uuid"]
        logging.info("Current config main mcu UUID : " + MAIN_MCU_UUID)

    if not KLIPPER_CONFIG.has_option(SERVICE_CONFIG["deviceConfigName"],"canbus_uuid"):
        logging.error("Invalid klipper config : [" + SERVICE_CONFIG["deviceConfigName"] + "]")
        sys.exit(1)
    else:
        CURRENT_TOOLHEAD_UUID = KLIPPER_CONFIG[SERVICE_CONFIG["deviceConfigName"]]["canbus_uuid"]
        logging.info("Current config toolhead mcu UUID : " + CURRENT_TOOLHEAD_UUID)

    success, deviceUUIDs = getCanDeviceUUIDs(SERVICE_CONFIG["scannerPath"],SERVICE_CONFIG["scanTimeout"])
    if not success:
        logging.error("CAN device UUID not found")
        sys.exit(1)
    if len(deviceUUIDs) < 1:
        logging.info("No CAN device found.")
        sys.exit(0)
    else:
        logging.info("Found devices : " + str(deviceUUIDs))


    DEVICE_FOUND = 0
    NEW_TOOLHEAD_UUID = ""
    for UUID in deviceUUIDs:
        if (UUID != MAIN_MCU_UUID) and (UUID != CURRENT_TOOLHEAD_UUID) and (UUID not in SERVICE_CONFIG["blackList"]) and (len(SERVICE_CONFIG["whiteList"]) == 0 or (UUID in SERVICE_CONFIG["whiteList"])):
            DEVICE_FOUND = DEVICE_FOUND + 1
            NEW_TOOLHEAD_UUID = UUID


    if DEVICE_FOUND == 0:
        logging.info("No suitable CAN device was found, or the device is already configured")
        sys.exit(0)

    if DEVICE_FOUND > 1:
        logging.error(str(DEVICE_FOUND) + " devices were found, but it cannot be determined which one is the correct device.")
        sys.exit(1)

    # update the config 
    logging.info("Found suitable device UUID : " + NEW_TOOLHEAD_UUID)
    KLIPPER_CONFIG[SERVICE_CONFIG["deviceConfigName"]]["canbus_uuid"] = NEW_TOOLHEAD_UUID

    # write config file
    success = writeKlipperConfig(KLIPPER_CONFIG,SAVED_CONFIG,SERVICE_CONFIG["klipperConfigFile"])
    if success:
        logging.info("Klipper configuration file updated successfully.")
    else:
        logging.error("Cannot update klipper configfile.")
        sys.exit(1)

    if SERVICE_CONFIG["restartKlipper"]:
        logging.info("Restarting klipper...")
        success = restartKlipper()
        if not success:
            logging.error("Cannot restart klipper service.")
            sys.exit(1)

    logging.info("New toolhead UUID has been updated : " + NEW_TOOLHEAD_UUID)
    logging.info("Done!")
    return 0


if __name__ == "__main__":
    main()
