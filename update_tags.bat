@echo off

echo Update the id3 tags of all .mp3 files in a folder.

call %homedrive%%homepath%\anaconda3\Scripts\activate.bat && call activate lib_dl

if not %errorlevel% == 0 (
echo There was an error initializing the conda environment.
echo Please make sure you have conda installed and create the lib_dl environment using the following command:
echo conda env create -f lib_dl.yml
goto end
)

set DEFAULT_FOLDER=..\dj
set /p target="Enter folder containing music, or leave blank to use default folder (%DEFAULT_FOLDER%): "
call python update_tags.py %target%
call conda deactivate
echo Finished.

:end
pause >nul
