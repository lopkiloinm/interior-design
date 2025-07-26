@echo off

echo Starting Interior Design Agent...

REM Start backend
echo Starting backend server...
cd backend
if not exist .venv (
    python -m venv .venv
    call .venv\Scripts\activate
pip install -r requirements.txt
)
call .venv\Scripts\activate
start cmd /k python main.py

REM Start frontend
echo Starting frontend...
cd ..\frontend
call npm install
start cmd /k npm run dev

echo.
echo Backend running on http://localhost:8000
echo Frontend running on http://localhost:5173
echo.
echo Close the command windows to stop the servers
pause 