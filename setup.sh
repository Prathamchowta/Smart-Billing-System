#!/bin/bash

# Smart Billing System - Setup Script
# This script helps you set up the entire project

echo "=========================================="
echo "Smart Billing System - Setup Guide"
echo "=========================================="
echo ""

# Step 1: Check Node.js installation
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null
then
    echo "❌ Node.js is not installed. Please install Node.js from https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js version: $(node -v)"
echo "✅ NPM version: $(npm -v)"
echo ""

# Step 2: Setup Backend
echo "=========================================="
echo "Setting up Backend..."
echo "=========================================="
cd backend

echo "Installing backend dependencies..."
npm install

echo ""
echo "Creating backend .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your Supabase credentials"
    echo "   - SUPABASE_URL: Your Supabase project URL"
    echo "   - SUPABASE_ANON_KEY: Your Supabase anonymous key"
else
    echo "✅ .env file already exists"
fi

cd ..
echo ""

# Step 3: Setup Frontend
echo "=========================================="
echo "Setting up Frontend..."
echo "=========================================="
cd frontend

echo "Installing frontend dependencies..."
npm install

echo ""
echo "Creating frontend .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit frontend/.env with your configuration"
    echo "   - REACT_APP_API_URL: Backend API URL (default: http://localhost:5000)"
    echo "   - REACT_APP_SUPABASE_URL: Your Supabase project URL"
    echo "   - REACT_APP_SUPABASE_ANON_KEY: Your Supabase anonymous key"
else
    echo "✅ .env file already exists"
fi

cd ..
echo ""

# Step 4: Summary
echo "=========================================="
echo "Setup Complete! ✅"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set up Supabase database:"
echo "   - Go to https://supabase.com"
echo "   - Create a new project"
echo "   - Go to SQL Editor and run the setup.sql script"
echo "   - Copy your project URL and Anon Key"
echo ""
echo "2. Update environment files:"
echo "   - Edit backend/.env with your Supabase credentials"
echo "   - Edit frontend/.env with your API URL and Supabase credentials"
echo ""
echo "3. Start the application:"
echo "   - Terminal 1: cd backend && npm run dev"
echo "   - Terminal 2: cd frontend && npm start"
echo ""
echo "4. Access the application:"
echo "   - Backend: http://localhost:5000"
echo "   - Frontend: http://localhost:3000"
echo ""
