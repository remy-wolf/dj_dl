@echo off

echo Download a YouTube video or playlist as .mp3s.

call %homedrive%%homepath%\anaconda3\Scripts\activate.bat && call activate lib_dl

if not %errorlevel% == 0 (
echo There was an error initializing the conda environment.
echo Please make sure you have conda installed and create the lib_dl environment using the following command:
echo conda env create -f lib_dl.yml
goto end
)

set /p target="Enter playlist or videos to download: "
call python download.py %target%
call conda deactivate
echo Finished.

:end
pause >nul
