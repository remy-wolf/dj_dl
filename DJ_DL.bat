@echo off

call %homedrive%%homepath%\anaconda3\Scripts\activate.bat && call activate lib_dl

if not %errorlevel% == 0 (
echo There was an error initializing the conda environment.
echo Please make sure you have conda installed and create the lib_dl environment running the following command in this directory:
echo conda env create -f lib_dl.yml
goto end
)

call python src\main.py
call conda deactivate

:end
pause >nul
