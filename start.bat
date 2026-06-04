@echo off
echo ========================================
echo   OpUnit - Demarrage du serveur
echo ========================================
echo.

REM Tuer les anciens processus Python
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2>nul
timeout /t 1 /nobreak >nul

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

REM Demarrer le serveur
echo Demarrage du serveur Flask...
echo.
echo ========================================
echo   URL: http://localhost:5000
echo ========================================
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

python app.py

pause
