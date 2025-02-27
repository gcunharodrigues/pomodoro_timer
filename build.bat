@echo off
echo Installing requirements...
pip install -r requirements.txt

echo Building executable...
pyinstaller --onefile --noconsole --name PomodoroTimer --icon=pomodoro.ico main.py

echo Build complete! Executable is in the dist folder.
pause 