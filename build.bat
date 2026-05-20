@echo off
echo Building 2048.exe...
pyinstaller --onefile --windowed --name 2048 game.py
echo.
echo Done! Output: dist\2048.exe
pause
