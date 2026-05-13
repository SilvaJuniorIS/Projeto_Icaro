@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo Icaro - Inicializador Local
echo ========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo Criando ambiente virtual local...
    py -3 -m venv venv
    if errorlevel 1 (
        echo Nao foi possivel criar o ambiente virtual.
        echo Instale Python 3.10+ e tente novamente.
        pause
        exit /b 1
    )
)

echo Instalando/atualizando dependencias...
"venv\Scripts\python.exe" -m pip install --upgrade pip
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo Iniciando Icaro em http://127.0.0.1:8100
echo Hub AtlasNex: http://127.0.0.1:8100/atlasnex
echo.
start "" "http://127.0.0.1:8100"
"venv\Scripts\python.exe" -m uvicorn api:app --host 127.0.0.1 --port 8100

pause
