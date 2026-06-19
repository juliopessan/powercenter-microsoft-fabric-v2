@echo off
REM Script wrapper para executar o PowerShell (compatível com CMD)
REM Uso: run-informatica-poc.bat [emp|hr|all]

setlocal enabledelayedexpansion

cd /d "%~dp0"

if "%1"=="" (
    set WORKFLOW_TYPE=all
) else (
    set WORKFLOW_TYPE=%1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  INFORMATICA POWERCENTER - POC EXECUTION                  ║
echo ║  Workflow Type: %WORKFLOW_TYPE%
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar se PowerShell está disponível
where pwsh.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] PowerShell 7+ não encontrado. Tentando PowerShell 5...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "run-informatica-poc.ps1" -WorkflowType "%WORKFLOW_TYPE%"
) else (
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "run-informatica-poc.ps1" -WorkflowType "%WORKFLOW_TYPE%"
)

set EXIT_CODE=%ERRORLEVEL%

echo.
echo Execução concluída com código de saída: %EXIT_CODE%
pause

exit /b %EXIT_CODE%
