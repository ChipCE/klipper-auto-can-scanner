import sys
import os
import shutil
from datetime import datetime
import json
import configparser
import subprocess
import logging

VERSION = "1.0rc1-20250119"
CONFIG_FILE = "./config.json"
LOG_FILE = "klipper-auto-can-scanner.log"
LOG_LEVEL = logging.INFO



def backupKlipperConfig(configFile):
    savePath = str(os.path.dirname(configFile)) + "/" + "klipper-auto-can-scanner_backup-" + datetime.now().strftime('%Y%m%d-%H%M') + "_printer.cfg"
    logging.info("Save printer.cfg backup as " + savePath)
    try:
        shutil.copy(configFile, savePath)
        return True
    except Exception as e:
        logging.error("Failed to save printer.cfg backup. Error : " + str(e))
        return False

print(backupKlipperConfig("/home/chip/Data/Code/klipper-auto-can-scanner/sample/printer.cfg"))