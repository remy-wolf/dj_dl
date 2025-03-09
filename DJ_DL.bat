@echo off

call .venv\Scripts\activate

if not %errorlevel% == 0 (
echo There was an error initializing the virtual environment.
echo Please make sure you have python installed and have created/initialized the virtual environment:
echo python -m venv .venv --prompt dj_dl
echo .venv\Scripts\activate
echo python -m pip install -r requirements.txt
goto end
)

:: Check for updates
git remote update >nul 2>&1
for /f %%i in ('git rev-parse @') do set LOCAL=%%i
for /f %%i in ('git rev-parse @{u}') do set REMOTE=%%i

if not "%LOCAL%" == "%REMOTE%" (
    set /p REPLY="An update is available. Would you like to install it? (y/N) "
    if /i "%REPLY%" == "y" (
        :: Download the installer
        powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/remy-wolf/dj_dl/main/DJ_DL_installer.bat'"
        :: Run the installer
        start /wait "" DJ_DL_installer.bat
        echo Update installed successfully! Please restart the program for changes to take effect.
        pause
        exit
    )
)

call python src\main.py
call deactivate

:end
pause >nul
