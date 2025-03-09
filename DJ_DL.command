#!/bin/bash

# Get the directory where this script is located
cd "$(dirname "$0")"

# Get branch from config using grep and sed
BRANCH=$(grep "git_branch" config/config.json | sed -E 's/.*"git_branch"[^"]*"([^"]+)".*/\1/') || BRANCH="main"

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

# Check for updates
git remote update > /dev/null 2>&1
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "${LOCAL}" != "${REMOTE}" ]; then
    read -p "An update is available. Would you like to install it? (y/N) " -n 1 -r
    echo
    if [[ "${REPLY}" =~ ^[Yy]$ ]]; then
        # Download the installer
        curl -s https://raw.githubusercontent.com/remy-wolf/dj_dl/main/DJ_DL_installer.sh -o DJ_DL_installer.sh
        chmod +x DJ_DL_installer.sh
        # Run the installer
        ./DJ_DL_installer.sh
        echo "Update installed successfully! Please restart the program for changes to take effect."
        read -n 1 -s -r -p "Press any key to exit..."
        exit 0
    fi
fi

python src/main.py
deactivate

# Keep terminal window open until key press
read -n 1 -s -r -p "" 