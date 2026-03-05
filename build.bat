@echo off
REM Build a single-file Windows executable with PyInstaller
REM Run this from the project root (where run_app.py and app.py live)

REM Activate your virtualenv or conda environment first
REM Example (PowerShell): `conda activate <env>`

pyinstaller --noconfirm --clean --onefile --windowed \
  --add-data "templates;templates" \
  --add-data "todo.db;." \
  run_app.py

echo Build complete. Check the `dist` folder for run_app.exe
pause
