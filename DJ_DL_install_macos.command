#!/bin/bash

# Get the directory where this script is located
cd "$(dirname "$0")"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git first."
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python first."
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi

# Check for ffmpeg/ffprobe
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg is not installed. Attempting to install..."
    
    # Detect OS and package manager
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "Please install Homebrew first: https://brew.sh/"
            read -n 1 -s -r -p "Press any key to exit..."
            exit 1
        fi
    else
        # Linux
        if command -v apt &> /dev/null; then
            # Debian/Ubuntu
            echo "This will require sudo privileges to install ffmpeg"
            sudo apt update && sudo apt install -y ffmpeg
        elif command -v dnf &> /dev/null; then
            # Fedora
            sudo dnf install -y ffmpeg
        elif command -v pacman &> /dev/null; then
            # Arch
            sudo pacman -S --noconfirm ffmpeg
        else
            echo "Could not detect package manager. Please install ffmpeg manually."
            read -n 1 -s -r -p "Press any key to exit..."
            exit 1
        fi
    fi
fi

# Check if this is an update (directory already exists)
if [ -d "$HOME/DJ_DL/.git" ]; then
    install_dir="$HOME/DJ_DL"
    echo "Updating existing installation..."
else
    # Function to prompt for directory
    get_install_directory() {
        while true; do
            read -p "Enter installation directory (leave empty for $HOME/DJ_DL): " install_dir
            
            # Use default if empty
            if [ -z "$install_dir" ]; then
                install_dir="$HOME/DJ_DL"
            fi
            
            # Expand ~ to $HOME if present
            install_dir="${install_dir/#\~/$HOME}"
            
            # Try to create directory
            if mkdir -p "$install_dir" 2>/dev/null; then
                # Check if directory is writable
                if [ -w "$install_dir" ]; then
                    break
                else
                    echo "Directory is not writable. Please choose another location."
                fi
            else
                echo "Invalid directory path. Please try again."
            fi
        done
        echo "$install_dir"
    }

    # Get installation directory
    install_dir=$(get_install_directory)
fi

cd "$install_dir"

# Clone or update repository
if [ ! -d ".git" ]; then
    echo "Performing fresh installation..."
    git clone https://github.com/remy-wolf/dj_dl.git .
else
    echo "Updating from repository..."
    git fetch
    git reset --hard origin/main
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv --prompt dj_dl
fi
source .venv/bin/activate

# Update pip and install/update dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --upgrade

# Create/update desktop shortcut
desktop_file="$HOME/Desktop/DJ_DL.desktop"
echo "[Desktop Entry]
Name=DJ_DL
Exec=bash $install_dir/DJ_DL.sh
Type=Application
Terminal=true" > "$desktop_file"
chmod +x "$desktop_file"

# Self-destruct this installer
rm -- "$0"

# Launch the program
bash DJ_DL.sh 