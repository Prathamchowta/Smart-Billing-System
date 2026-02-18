@echo off
REM Smart Billing System - Windows Setup Script

echo.
echo ==========================================
echo Smart Billing System - Setup Guide
echo ==========================================
echo.

REM Step 1: Check Node.js installation
echo Checking Node.js installation...
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [FAILED] Node.js is not installed.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js is installed
node --version
npm --version
echo.

REM Step 2: Setup Backend
echo ==========================================
echo Setting up Backend...
echo ==========================================
cd backend

echo Installing backend dependencies...
call npm install

echo.
echo Creating backend .env file...
if not exist .env (
    copy .env.example .env
    echo [WARNING] Please edit backend\.env with your Supabase credentials
    echo   - SUPABASE_URL: Your Supabase project URL
    echo   - SUPABASE_ANON_KEY: Your Supabase anonymous key
) else (
    echo [OK] .env file already exists
)

cd ..
echo.

REM Step 3: Setup Frontend
echo ==========================================
echo Setting up Frontend...
echo ==========================================
cd frontend

echo Installing frontend dependencies...
call npm install

echo.
echo Creating frontend .env file...
if not exist .env (
    copy .env.example .env
    echo [WARNING] Please edit frontend\.env with your configuration
    echo   - REACT_APP_API_URL: Backend API URL (default: http://localhost:5000^)
    echo   - REACT_APP_SUPABASE_URL: Your Supabase project URL
    echo   - REACT_APP_SUPABASE_ANON_KEY: Your Supabase anonymous key
) else (
    echo [OK] .env file already exists
)

cd ..
echo.

REM Step 4: Summary
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Set up Supabase database:
echo    - Go to https://supabase.com
echo    - Create a new project
echo    - Go to SQL Editor and run setup.sql script
echo    - Copy your project URL and Anon Key
echo.
echo 2. Update environment files:
echo    - Edit backend\.env with your Supabase credentials
echo    - Edit frontend\.env with your API URL and Supabase credentials
echo.
echo 3. Start the application:
echo    - Terminal 1: cd backend ^&^& npm run dev
echo    - Terminal 2: cd frontend ^&^& npm start
echo.
echo 4. Access the application:
echo    - Backend: http://localhost:5000
echo    - Frontend: http://localhost:3000
echo.
pause
