#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

if [ $? -ne 0 ]; then
    echo "There was an error initializing the virtual environment."
    echo "Please make sure you have python installed and have created/initialized the virtual environment:"
    echo "python3 -m venv .venv --prompt dj_dl"
    echo "source .venv/bin/activate"
    echo "python -m pip install -r requirements.txt"
    exit 1
fi

python src/main.py
deactivate

# Keep terminal window open until key press
read -n 1 -s -r -p "" 