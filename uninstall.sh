#!/bin/bash
sudo systemctl stop klipper-auto-can-scanner
sudo rm /etc/systemd/system/klipper-auto-can-scanner.service
sudo systemctl daemon-reload
echo "Done"