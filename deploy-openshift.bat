@echo off
setlocal enabledelayedexpansion

REM OpenShift Deployment Script for Phone Selector App
REM ==================================================

set PROJECT_NAME=phone-selector
set APP_NAME=phone-selector
set GIT_REPO=https://github.com/giomara-larraga/researchers-night.git

echo 🚀 OpenShift Deployment Script for Phone Selector App
echo ========================================================

REM Check if oc CLI is installed
where oc >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ OpenShift CLI (oc) is not installed or not in PATH
    echo ℹ️  Please install it from: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html
    exit /b 1
)
echo ✅ OpenShift CLI found

REM Check if logged into OpenShift
oc whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Not logged into OpenShift cluster
    echo ℹ️  Please run: oc login ^<your-cluster-url^>
    exit /b 1
)
echo ✅ Logged into OpenShift

if "%1"=="deploy" goto :deploy
if "%1"=="status" goto :status
if "%1"=="logs" goto :logs
if "%1"=="url" goto :url
if "%1"=="build" goto :build
if "%1"=="clean" goto :clean
if "%1"=="help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--help" goto :help
if "%1"=="" goto :deploy
goto :unknown

:deploy
echo ℹ️  Starting deployment...

REM Setup project
echo ℹ️  Setting up project: %PROJECT_NAME%
oc get project %PROJECT_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    echo ℹ️  Project %PROJECT_NAME% already exists, switching to it
    oc project %PROJECT_NAME%
) else (
    echo ℹ️  Creating new project: %PROJECT_NAME%
    oc new-project %PROJECT_NAME% --display-name="Phone Selector App" --description="Multi-criteria phone selection application"
)
echo ✅ Project %PROJECT_NAME% is ready

REM Deploy using template if available
if exist "openshift\template.yaml" (
    echo ℹ️  Deploying application using template...
    oc process -f openshift/template.yaml -p APP_NAME=%APP_NAME% -p GIT_REPO=%GIT_REPO% -p MEMORY_LIMIT=512Mi -p CPU_LIMIT=500m | oc apply -f -
    echo ✅ Application deployed using template
) else (
    echo ℹ️  Deploying individual OpenShift resources...
    
    if exist "openshift\imagestream.yaml" oc apply -f openshift/imagestream.yaml
    if exist "openshift\buildconfig.yaml" oc apply -f openshift/buildconfig.yaml
    if exist "openshift\configmap.yaml" oc apply -f openshift/configmap.yaml
    if exist "openshift\deployment.yaml" oc apply -f openshift/deployment.yaml
    if exist "openshift\service.yaml" oc apply -f openshift/service.yaml
    if exist "openshift\route.yaml" oc apply -f openshift/route.yaml
    
    echo ✅ All resources deployed
)

REM Start build
echo ℹ️  Starting build process...
oc get bc phone-selector-build >nul 2>&1
if %errorlevel% equ 0 (
    oc start-build phone-selector-build --follow
) else (
    oc get bc %APP_NAME% >nul 2>&1
    if %errorlevel% equ 0 (
        oc start-build %APP_NAME% --follow
    ) else (
        echo ⚠️  No build config found, build will be triggered automatically
    )
)

REM Wait for deployment
echo ℹ️  Waiting for deployment to be ready...
oc rollout status deployment/%APP_NAME% --timeout=300s
echo ✅ Deployment is ready

REM Get application URL
call :get_url

echo.
echo ✅ 🎉 Deployment completed successfully!
echo.
call :show_status
goto :end

:status
echo ℹ️  Deployment Status:
echo ==================
echo.
echo ℹ️  Pods:
oc get pods -l app=%APP_NAME%
echo.
echo ℹ️  Services:
oc get svc -l app=%APP_NAME%
echo.
echo ℹ️  Routes:
oc get routes -l app=%APP_NAME%
echo.
echo ℹ️  Builds:
oc get builds
goto :end

:logs
echo ℹ️  Application logs:
for /f "tokens=*" %%i in ('oc get pods -l app=%APP_NAME% -o jsonpath="{.items[0].metadata.name}" 2^>nul') do set POD_NAME=%%i
if defined POD_NAME (
    oc logs -f %POD_NAME%
) else (
    echo ❌ No running pods found
)
goto :end

:url
call :get_url
goto :end

:build
echo ℹ️  Starting build...
oc get bc phone-selector-build >nul 2>&1
if %errorlevel% equ 0 (
    oc start-build phone-selector-build --follow
) else (
    oc get bc %APP_NAME% >nul 2>&1
    if %errorlevel% equ 0 (
        oc start-build %APP_NAME% --follow
    ) else (
        echo ❌ No build config found
    )
)
goto :end

:clean
echo ⚠️  Cleaning up deployment...
oc delete all -l app=%APP_NAME%
oc delete configmap -l app=%APP_NAME%
oc delete route -l app=%APP_NAME%
echo ✅ Cleanup completed
goto :end

:get_url
echo ℹ️  Getting application URL...
oc get route phone-selector-route >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('oc get route phone-selector-route -o jsonpath="{.spec.host}" 2^>nul') do set APP_URL=%%i
) else (
    oc get route %APP_NAME% >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=*" %%i in ('oc get route %APP_NAME% -o jsonpath="{.spec.host}" 2^>nul') do set APP_URL=%%i
    )
)
if defined APP_URL (
    echo ✅ Application URL: https://!APP_URL!
    echo.
    echo ℹ️  🌐 Your Phone Selector app is available at: https://!APP_URL!
) else (
    echo ⚠️  No route found
)
goto :eof

:show_status
echo ℹ️  Deployment Status:
echo ==================
echo.
echo ℹ️  Pods:
oc get pods -l app=%APP_NAME%
echo.
echo ℹ️  Services:
oc get svc -l app=%APP_NAME%
echo.
echo ℹ️  Routes:
oc get routes -l app=%APP_NAME%
goto :eof

:help
echo OpenShift Deployment Script for Phone Selector App
echo.
echo Usage: %0 [command]
echo.
echo Commands:
echo   deploy  - Deploy the application (default)
echo   status  - Show deployment status
echo   logs    - Show application logs
echo   url     - Get application URL
echo   build   - Start a new build
echo   clean   - Clean up deployment
echo   help    - Show this help message
goto :end

:unknown
echo ❌ Unknown command: %1
echo ℹ️  Use '%0 help' for usage information
exit /b 1

:end
endlocal