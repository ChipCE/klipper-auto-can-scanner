#!/bin/bash

ENV_NAME="tets-venv"

currentPath=${PWD}
cd "$currentPath"
python3 -m venv "$ENV_NAME"
cd "$ENV_NAME/bin"
chmod +x activate
source activate
cd "$currentPath"
pip install -r requirements.txt