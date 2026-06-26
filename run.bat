@echo off
title Heaven Leaves - Local Server
echo ================================
echo   Heaven Leaves Development Server
echo ================================
echo.
echo Starting server at http://127.0.0.1:8000/
echo Admin panel: http://127.0.0.1:8000/admin/
echo Admin login: admin / Admin@1234
echo.
echo Press CTRL+C to stop the server
echo.
cd /d %~dp0
.\venv\Scripts\python.exe manage.py runserver 8000
pause
