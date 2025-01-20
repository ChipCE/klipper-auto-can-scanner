#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

sudo apt-get update
sudo apt-get install net-tools python3 python3-pip python3-venv

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

yes | sudo cp -rf klipper-auto-can-scanner.service /etc/systemd/system/klipper-auto-can-scanner.service

chmod +x ./scan.sh

sudo systemctl daemon-reload
sudo systemctl start klipper-auto-can-scanner
# this service does not need to be run at startup
# sudo systemctl enable klipper-auto-can-scanner
 
