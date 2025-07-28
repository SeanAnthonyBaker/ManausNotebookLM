@echo off
echo.
echo ^> Stopping NotebookLM Automation Services...
docker-compose down --remove-orphans
echo.
echo ^> All services stopped successfully.