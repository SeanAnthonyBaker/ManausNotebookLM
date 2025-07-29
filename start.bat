@echo off
setlocal enabledelayedexpansion

:: Set the working directory to the script's location to ensure relative paths work correctly.
pushd "%~dp0"
set "SCRIPT_DIR=%CD%"

echo.
echo ^> Starting NotebookLM Automation Services...
echo.

REM --- Pre-flight check for .env file ---
IF NOT EXIST ".env" (
    echo [ERROR] Configuration file '.env' not found in the script's directory: %SCRIPT_DIR%
    echo [ERROR] Please ensure it exists and contains the line: GCLOUD_CONFIG_PATH=./.gcloud
    popd
    pause
    exit /b 1
)

REM --- Robustly read GCLOUD_CONFIG_PATH from .env file ---
set "GCLOUD_PATH="
set "TEMP_ENV_FILE=%TEMP%\env_check.tmp"

REM Use the native findstr command, which is more reliable than PowerShell for this task in cmd.exe.
(findstr /B /I "GCLOUD_CONFIG_PATH=" ".env") > "%TEMP_ENV_FILE%" 2>nul

REM Parse the temp file using a FOR /F loop, which is the standard way to tokenize a line.
for /f "usebackq tokens=1,* delims==" %%a in ("%TEMP_ENV_FILE%") do (
    set "GCLOUD_PATH=%%~b"
)
if exist "%TEMP_ENV_FILE%" del "%TEMP_ENV_FILE%"

REM --- Validate the GCLOUD_CONFIG_PATH ---
if "%GCLOUD_PATH%" == "" (
    echo [ERROR] GCLOUD_CONFIG_PATH is not defined in your .env file.
    echo [ERROR] Please check your '.env' file in: %SCRIPT_DIR%
    echo [ERROR] Please ensure it contains the line: GCLOUD_CONFIG_PATH=./.gcloud
    popd
    pause
    exit /b 1
)

IF NOT EXIST "%GCLOUD_PATH%" (
    echo [ERROR] The gcloud credentials directory was not found at: %SCRIPT_DIR%\%GCLOUD_PATH%
    echo [ERROR] Please ensure you have created the '.gcloud' directory in your project root.
    popd
    pause
    exit /b 1
)

IF NOT EXIST "%GCLOUD_PATH%\credentials.db" (
    echo [ERROR] The 'credentials.db' file was not found inside '%GCLOUD_PATH%'.
    echo [ERROR] Please copy your gcloud credentials into the '.gcloud' directory.
    popd
    pause
    exit /b 1
)

echo [SUCCESS] All pre-flight checks passed.
echo.

echo ^> Building and starting services in the background...
docker-compose up --build -d

popd
endlocal
