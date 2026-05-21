@echo off
@REM ***************************************************************************
@REM * Script to handle python environment and startup given script
@REM ***************************************************************************
setlocal EnableDelayedExpansion
@REM ***************************************************************************
@REM * Set base variables, you may tweak here
@REM ***************************************************************************
@REM Set name of python environment
set "ENV_NAME=.venv"
@REM Set name of python environment list exported by pip freeze > %REQ_NAME%
set "REQ_NAME=requirements.txt"
@REM Get name of script to start
set "SCRIPT=%~1"
@REM Set default name of script to run
set "DEF_SCRIPT=program.py"
@REM ***************************************************************************
@REM * Set internal variables, don't touch unless you know what you're doing!
@REM ***************************************************************************
@REM Get startup path of script
set "PATH_BASE=%~dp0"
@REM Set FQN of environment
set "PATH_ENVIRONMENT=%PATH_BASE%%ENV_NAME%"
set "PATH_ACTIVATE=%PATH_ENVIRONMENT%\Scripts\activate.bat"
set "PATH_PYTHON=%PATH_ENVIRONMENT%\Scripts\python.exe"
@REM ***************************************************************************
@REM * Check environment for existence
@REM ***************************************************************************
if not exist "%PATH_ENVIRONMENT%" (
    @REM Create environment
    echo.Create missing environment [%ENV_NAME%]
    python -m venv "%PATH_ENVIRONMENT%"
    @REM Activate environment
    if ""=="%VIRTUAL_ENV%" (
        echo.Initial activation of environment [%ENV_NAME%]
        if exist "%PATH_ACTIVATE%" call "%PATH_ACTIVATE%"
    )
    @REM Install required modules
    if exist "%REQ_NAME%" (
        echo.Install required modules in [%REQ_NAME%] to [%ENV_NAME%]
        type "%REQ_NAME%"
        "%PATH_PYTHON%" -m pip install -r "%REQ_NAME%"
    ) else (
        echo.List of required modules [%REQ_NAME%] not found
    )
)
@REM ***************************************************************************
@REM * Activate environment if not already done
@REM ***************************************************************************
if ""=="%VIRTUAL_ENV%" (
    echo.Activate environment [%ENV_NAME%]
    if exist "%PATH_ACTIVATE%" call "%PATH_ACTIVATE%"
)
@REM ***************************************************************************
@REM * Handle special commands or determine script to run
@REM ***************************************************************************
if "%SCRIPT%"=="tests" (
    echo.Execute tests
    python -m unittest discover -s tests -p "test_*.py"
) else (
    @REM If no name is passed, set default value
    if "%SCRIPT%"=="" (
        echo.No script name passed, set default [%DEF_SCRIPT%]
        set "SCRIPT=%DEF_SCRIPT%"
    )
    set "SCRIPT_PATH=%PATH_BASE%!SCRIPT!"
    @REM ***************************************************************************
    @REM * Execute script
    @REM ***************************************************************************
    if exist "!SCRIPT_PATH!" (
        echo.Execute script [!SCRIPT!]
        "%PATH_PYTHON%" "!SCRIPT_PATH!"
    ) else (
        echo.Script [!SCRIPT!] not found :-()
    )
)
endlocal
