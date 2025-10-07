@echo off
echo ========================================
echo Starting Flask Backend on Port 16005
echo ========================================

REM Kill any existing backend on port 16005
echo Checking for existing backend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :16005') do (
    echo Stopping existing process %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Installing Flask dependencies...
cd backend
pip install -r requirements_flask.txt

echo.
echo Starting Flask backend...
python app_flask.py

