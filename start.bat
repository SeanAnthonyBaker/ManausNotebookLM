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
    echo [ERROR] Please copy your gcloud credentials from your system's gcloud config folder.
    echo [INFO]  On Windows, this is usually located at: %APPDATA%\gcloud
    echo [INFO]  Copy the contents of that folder into your project's '%GCLOUD_PATH%' directory.
    popd
    pause
    exit /b 1
)

echo [SUCCESS] All pre-flight checks passed.
echo.

echo ^> Building and starting services in the background...
docker-compose up --build -d

echo.
echo ^> Waiting for services to become healthy...

set "HEALTHY=false"
for /l %%i in (1,1,30) do (
    set "SELENIUM_STATUS="
    REM Get selenium container ID and then inspect it. This avoids using 'xargs', which is not native to Windows.
    for /f "tokens=*" %%c in ('docker-compose ps -q selenium 2^>nul') do (
        for /f "tokens=*" %%s in ('docker inspect -f "{{.State.Health.Status}}" %%c 2^>nul') do (
            set "SELENIUM_STATUS=%%s"
        )
    )

    echo !SELENIUM_STATUS! | findstr /I "healthy" >nul
    if !errorlevel! equ 0 (
        set "APP_STATUS="
        REM Get app container ID and then inspect it.
        for /f "tokens=*" %%d in ('docker-compose ps -q app 2^>nul') do (
            for /f "tokens=*" %%a in ('docker inspect -f "{{.State.Health.Status}}" %%d 2^>nul') do (
                set "APP_STATUS=%%a"
            )
        )
        echo !APP_STATUS! | findstr /I "healthy" >nul
        if !errorlevel! equ 0 (
            set "HEALTHY=true"
            goto :services_ready
        )
    )
    REM Use set /p to print a character without a newline in cmd.exe
    <nul set /p =.
    timeout /t 2 /nobreak >nul
)

:services_ready
echo.
if "%HEALTHY%"=="true" (
    echo [SUCCESS] All services are healthy and running!
    echo.
    echo [INFO] Service URLs:
    echo [INFO]   - Flask API: http://localhost:5000
    echo [INFO]   - API Status: http://localhost:5000/api/get_status
    echo [INFO]   - VNC Viewer: http://localhost:7900 (password: secret)
    goto :end_script
) else (
    echo.
    echo [ERROR] One or more services failed to become healthy in time.
    echo [INFO]  Displaying final service status:
    docker-compose ps
    echo.
    echo [INFO]  Displaying recent logs for the failing 'selenium' service:
    echo ----------------------------------------------------------------------
    docker-compose logs --tail="50" selenium
    echo ----------------------------------------------------------------------
    echo [INFO]  Please check the logs above for the specific error.
)

:end_script
popd
endlocal
