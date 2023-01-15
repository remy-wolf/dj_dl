@echo off

call D:\anaconda3\Scripts\activate.bat
call activate lib_fix

set /p "target=Enter playlist or videos to download: "

python download.py %target%

call conda deactivate

echo Finished.
pause
