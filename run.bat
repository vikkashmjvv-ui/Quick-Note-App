@echo off
cd /d "%~dp0"
echo ============================================
echo   Quick Note App - Setting up and running
echo ============================================
echo.
echo Installing required packages...
pip install -r requirements.txt
echo.
echo Starting the app...
echo Open your browser and go to: http://127.0.0.1:5000
echo (Do not close this window while using the app)
echo.
python app.py
pause
