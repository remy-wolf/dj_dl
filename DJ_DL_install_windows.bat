@echo off
setlocal EnableDelayedExpansion

:: Check if git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check for ffmpeg/ffprobe
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing ffmpeg...
    :: Get latest release URL
    powershell -Command "$releases = Invoke-RestMethod -Uri 'https://api.github.com/repos/GyanD/codexffmpeg/releases/latest'; $asset = $releases.assets | Where-Object { $_.name -like '*full_build.zip' } | Select-Object -First 1; Invoke-WebRequest -Uri $asset.browser_download_url -OutFile 'ffmpeg.zip'"
    
    :: Extract ffmpeg
    echo Extracting ffmpeg...
    powershell -Command "$shell = New-Object -ComObject Shell.Application; $zip = $shell.NameSpace((Resolve-Path 'ffmpeg.zip').Path); $dest = $shell.NameSpace((Resolve-Path '.').Path); $dest.CopyHere($zip.Items(), 0x14)"
    
    :: Find the extracted directory (it will be the only ffmpeg-* directory)
    for /d %%i in (ffmpeg-*) do set "ffmpeg_dir=%%i"
    
    :: Move binaries to Windows directory (requires admin)
    echo Moving ffmpeg binaries to System32...
    move /y "!ffmpeg_dir!\bin\*" "%SystemRoot%\System32\"
    
    :: Clean up
    rmdir /s /q "!ffmpeg_dir!"
    del ffmpeg.zip
    echo FFmpeg installation complete.
)

:: Check if this is an update (directory already exists)
if exist "%USERPROFILE%\DJ_DL\.git" (
    set "install_dir=%USERPROFILE%\DJ_DL"
    echo Updating existing installation...
) else (
    :: Prompt for installation directory
    :ask_directory
    set "install_dir="
    set /p "install_dir=Enter installation directory (leave empty for %USERPROFILE%\DJ_DL): "

    :: Use default if empty
    if "!install_dir!"=="" set "install_dir=%USERPROFILE%\DJ_DL"

    :: Check if path is valid and create directory
    mkdir "!install_dir!" 2>nul
    if %errorlevel% neq 0 (
        echo Invalid directory path. Please try again.
        goto ask_directory
    )
)

:: Navigate to installation directory
cd /d "!install_dir!"

:: Clone or update repository
if not exist ".git" (
    echo Performing fresh installation...
    git clone https://github.com/remy-wolf/dj_dl.git .
) else (
    echo Updating from repository...
    git fetch
    git reset --hard origin/main
)

:: Create and activate virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv --prompt dj_dl
)
call .venv\Scripts\activate

:: Update pip and install/update dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --upgrade

:: Create/update desktop shortcut
echo Updating desktop shortcut...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\DJ_DL.lnk'); $SC.TargetPath = '!install_dir!\DJ_DL.bat'; $SC.Save()"

:: Self-destruct this installer
(goto) 2>nul & del "%~f0"

:: Launch the program
call DJ_DL.bat 