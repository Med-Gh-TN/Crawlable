@echo off
TITLE Crowable SOTA Pipeline
CLS

echo ========================================================
echo             CROWABLE - SOTA CODE EXTRACTOR
echo ========================================================
echo.

:: Prompt the user for the path
set /p TARGET_PATH="Please enter the FULL PATH to the project folder: "

:: Strip out any existing quotes if the user accidentally pasted them
set TARGET_PATH=%TARGET_PATH:"=%

echo.
echo [INFO] Starting pipeline for: "%TARGET_PATH%"
echo --------------------------------------------------------

:: Call the new main entry point
python main.py "%TARGET_PATH%"

echo.
echo --------------------------------------------------------
echo [INFO] Execution finished.
pause