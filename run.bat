@echo off
echo Installing required Python packages...
pip install -r requirements.txt

echo.
echo Running bill_utility_gui.py...

:: Try running with python first
python bill_utility_gui.py
IF %ERRORLEVEL% NEQ 0 (
    echo Python command failed, trying with py...
    py bill_utility_gui.py
)

pause
