@echo off

echo Download a Spotify playlist as .mp3s by searching YouTube for matching songs.
echo NOTE: This is still experimental.

call %homedrive%%homepath%\anaconda3\Scripts\activate.bat && call activate lib_dl

if not %errorlevel% == 0 (
echo There was an error initializing the conda environment.
echo Please make sure you have conda installed and create the lib_dl environment using the following command:
echo conda env create -f lib_dl.yml
goto end
)

call python scripts\scrape_spotify.py
call conda deactivate
echo Finished.

:end
pause >nul
