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
SAVED_CONFIG = []

logging.basicConfig(level=LOG_LEVEL,  handlers=[logging.FileHandler(LOG_FILE, mode='w'), logging.StreamHandler()], format="%(asctime)-15s %(levelname)-8s %(message)s")

def readKlipperConfig(configFile):
    try:
        config = configparser.ConfigParser(delimiters=(':','='))
        config.read(configFile)
        if len(config.sections()) == 0:
            return False, None
        return True, config
    except Exception as e:
        logging.error("\t" + str(e))
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
        logging.warning("Cannot load saved config!")
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


def readConfig(configFile):
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
        
            if type(serviceConfigJson["klipperVenvPath"]) != str or serviceConfigJson["klipperVenvPath"] == "":
                logging.error("Invalid config : klipperVenvPath")
                hasError = True

            if type(serviceConfigJson["restartKlipper"]) != bool:
                logging.error("Invalid config : restartKlipper")
                hasError = True

            if type(serviceConfigJson["canBus"]) != str or serviceConfigJson["canBus"] == "":
                logging.error("Invalid config : canBus")
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

            if type(serviceConfigJson["debug"]) != bool:
                logging.error("Invalid config : debug")
                hasError = True

            return not hasError,serviceConfigJson
    except Exception as e:
        logging.error("Failed to read service config : " + str(e))
        return False,None
    return False,None


# success, SERVICE_CONFIG = readConfig("./sample/config.json")
# # print(success,str(SERVICE_CONFIG))
# success, KLIPPER_CONFIG = readKlipperConfig("./sample/printer.cfg")
# success, SAVED_CONFIG = getSavedConfig("./sample/printer.cfg")

# # writeKlipperConfig(KLIPPER_CONFIG,SAVED_CONFIG,"./sample/copy.cfg")



# print(KLIPPER_CONFIG.has_option("mcu","serial2"))


a = "asdfghjkl"
b = ["as", "world", "test"]

# Check if any member of b is not a substring of a
result = any(item not in a for item in b)

print(result)