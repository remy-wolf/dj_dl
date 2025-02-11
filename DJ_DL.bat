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

call python src\main.py
call deactivate

:end
pause >nul
