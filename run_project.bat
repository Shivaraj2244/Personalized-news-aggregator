@echo off
title Personalized News Aggregator
echo ===========================================
echo     Starting Personalized News Project...
echo ===========================================

REM --- Start the Inshorts API Server ---
echo  Starting Inshorts API (Flask)...
start cmd /k "cd Inshorts-News-API && venv36\Scripts\activate && python main.py"

REM --- Start the Django Server ---
echo  Starting Django Server...
start cmd /k "cd . && venv\Scripts\activate && python manage.py runserver"

echo ===========================================
echo  Both servers are running! 
echo  Django: http://127.0.0.1:8000/
echo  API:    http://127.0.0.1:5000/
echo ===========================================
pause
