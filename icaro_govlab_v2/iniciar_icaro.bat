@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=..\venv\Scripts\python.exe"
set "HOST=127.0.0.1"
set "PORT=8010"
set "URL=http://%HOST%:%PORT%"

if not exist "%PYTHON_EXE%" (
  echo Python do ambiente virtual nao encontrado em %PYTHON_EXE%.
  echo Verifique se o ambiente virtual existe em C:\Projeto_Icaro\venv.
  pause
  exit /b 1
)

start "" "%URL%"
echo Iniciando Icaro GovLab v2 em %URL%
echo Para encerrar, feche esta janela ou pressione CTRL+C.

"%PYTHON_EXE%" -m uvicorn app.main:app --reload --host %HOST% --port %PORT%

pause
