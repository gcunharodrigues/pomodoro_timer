#!/bin/bash
echo "Installing requirements..."
pip3 install -r requirements.txt

echo "Building macOS executable..."
pyinstaller --onefile --noconsole --name PomodoroTimer --icon=pomodoro.ico main.py

echo "Build complete! Executable is in the dist folder." 