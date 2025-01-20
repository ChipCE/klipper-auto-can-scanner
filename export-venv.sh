#!/bin/bash
currentPath=${PWD}
cd "$currentPath"
python -m pip freeze > requirements.txt