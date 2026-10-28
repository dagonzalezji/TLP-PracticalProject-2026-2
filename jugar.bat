@echo off
cls

if "%~1"=="" (
    echo.
    echo   Uso: jugar.bat [nombre_del_juego]
    echo   Ejemplo: jugar.bat snake_evolved
    echo   Ejemplo: jugar.bat snake
    echo   Ejemplo: jugar.bat tetris
    echo.
    exit /b 1
)

set JUEGO=%~1
set ARCHIVO_BRICK=games\%JUEGO%.brick
set ARCHIVO_JSON=games\%JUEGO%.json

if not exist "%ARCHIVO_BRICK%" (
    echo Error: No existe el archivo %ARCHIVO_BRICK%
    exit /b 1
)

echo Compilando el juego: %JUEGO%...
echo ----------------------------------

python compiler.py "%ARCHIVO_BRICK%"
if %errorlevel% neq 0 (
    echo.
    echo !!! Ocurrio un error durante la compilacion. !!!
    exit /b 1
)

echo.
echo Compilacion exitosa. Iniciando el juego...
echo ----------------------------------

python runtime.py "%ARCHIVO_JSON%"

echo.
echo El juego ha finalizado.
