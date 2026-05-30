@echo off
cd /d "%~dp0"

echo Installing PyInstaller...
py -3 -m pip install pyinstaller

echo Building game...
py -3 -m PyInstaller --onefile --name "GenshinSpire" --windowed --add-data "images;images" --add-data "audio;audio" main.py

echo Cleaning up...
if exist build (
    rmdir /s /q build
)
if exist GenshinSpire.spec (
    del GenshinSpire.spec
)

echo Done! Find the .exe in dist folder
pause
