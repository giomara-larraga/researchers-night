@echo off
setlocal

echo 🚀 Phone Selector App Deployment
echo ================================

if "%1"=="build" goto :build
if "%1"=="run" goto :run
if "%1"=="deploy" goto :deploy
if "%1"=="logs" goto :logs
if "%1"=="status" goto :status
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="clean" goto :clean
goto :usage

:build
echo 📦 Building Docker image...
docker build -t phone-selector-app .
if %errorlevel%==0 (
    echo ✅ Docker image built successfully!
) else (
    echo ❌ Failed to build Docker image
    exit /b 1
)
goto :end

:run
echo 🧹 Cleaning up existing container...
docker stop phone-selector >nul 2>&1
docker rm phone-selector >nul 2>&1
echo 🏃 Running container...
docker run -d --name phone-selector -p 8050:8050 --env DEBUG=false --restart unless-stopped phone-selector-app
if %errorlevel%==0 (
    echo ✅ Container started successfully!
    echo 🌐 App available at: http://localhost:8050
) else (
    echo ❌ Failed to start container
    exit /b 1
)
goto :end

:deploy
call :clean
call :build
if %errorlevel% neq 0 goto :end
call :run
goto :end

:logs
echo 📋 Container logs:
docker logs -f phone-selector
goto :end

:status
echo 📊 Container status:
docker ps -f name=phone-selector
goto :end

:stop
echo 🛑 Stopping container...
docker stop phone-selector
goto :end

:restart
echo 🔄 Restarting container...
docker restart phone-selector
goto :end

:clean
echo 🧹 Cleaning up existing container...
docker stop phone-selector >nul 2>&1
docker rm phone-selector >nul 2>&1
echo ✅ Cleanup completed
goto :end

:usage
echo Usage: %0 {build^|run^|deploy^|logs^|status^|stop^|restart^|clean}
echo.
echo Commands:
echo   build   - Build Docker image
echo   run     - Run container (stops existing first)
echo   deploy  - Build image and run container
echo   logs    - Show container logs
echo   status  - Show container status
echo   stop    - Stop container
echo   restart - Restart container
echo   clean   - Remove container
exit /b 1

:end
endlocal