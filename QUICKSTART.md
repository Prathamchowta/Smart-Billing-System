# Quick Start Guide

Get your Smart Billing System running in 5 minutes!

## Prerequisites
- Node.js 14+ installed ([Download](https://nodejs.org))
- A Supabase account (free at [supabase.com](https://supabase.com))

## Step 1: Create Supabase Project (2 minutes)

1. Go to https://supabase.com and sign up/login
2. Click "New Project"
3. Give it a name: "Smart Billing System"
4. Create a secure password
5. Wait for the project to initialize
6. Go to **Settings → API**
7. Copy your:
   - Project URL
   - Anon Key (public key)

## Step 2: Set Up Database (1 minute)

1. In Supabase, go to **SQL Editor**
2. Click **New Query**
3. Copy-paste all content from `database_setup.sql`
4. Click **Run**

✅ Your database is ready!

## Step 3: Configure Backend (1 minute)

```bash
cd backend

# Copy environment file
cp .env.example .env

# Edit .env and add your Supabase info:
# SUPABASE_URL=your_project_url_from_step_1
# SUPABASE_ANON_KEY=your_anon_key_from_step_1
```

## Step 4: Configure Frontend (30 seconds)

```bash
cd frontend

# Copy environment file
cp .env.example .env

# Edit .env:
# REACT_APP_API_URL=http://localhost:5000
# (Keep the two lines for Supabase URLs if you plan to use Supabase directly from frontend)
```

## Step 5: Install & Run

**Terminal 1 - Backend:**
```bash
cd backend
npm install
npm run dev
```
You should see: `Server running on port 5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```
Your browser will open to http://localhost:3000

## Step 6: Start Using!

### Dashboard
- View revenue statistics
- See recent bills
- Monitor business metrics

### Billing
- Select items from the menu
- Add customer name
- Create bill and print

### Menu
- Add new menu items
- Set prices
- Manage inventory

### Analytics
- View sales trends
- See top-selling items
- Get profit predictions

## Common Issues

### "Cannot find module" error
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port 5000 already in use
Edit `backend/.env`:
```
PORT=5001
```

Then update frontend `.env`:
```
REACT_APP_API_URL=http://localhost:5001
```

### CORS errors
Make sure backend is running on the URL specified in frontend's `.env`

### Database not connecting
Double-check `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) to deploy to production
- See [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) for differences from desktop version

## Need Help?

1. Check error messages in terminal/browser console
2. Verify all environment variables are set correctly
3. Ensure internet connection is working
4. Check Supabase status at https://status.supabase.com

## Development Tips

- **Hot Reload**: Both frontend and backend support hot reload during development
- **Database**: Supabase dashboard shows all data in real-time
- **API Testing**: Use Postman or curl to test backend endpoints
- **Browser DevTools**: Use F12 to debug frontend

## Useful Commands

```bash
# Start backend with auto-reload
npm run dev

# Start frontend development
npm start

# Build frontend for production
npm run build

# View Supabase logs
# (In Supabase dashboard → Logs)
```

## File Structure Quick Reference

```
Smart_Billing_System/
├── backend/                    # Node.js API server
│   ├── server.js              # Main server & routes
│   ├── package.json           # Backend dependencies
│   └── .env                   # Environment variables
│
├── frontend/                   # React web app
│   ├── src/
│   │   ├── pages/            # Page components
│   │   ├── services/         # API calls
│   │   ├── styles/           # CSS files
│   │   └── App.js            # Main component
│   ├── package.json          # Frontend dependencies
│   └── .env                  # Environment variables
│
├── database_setup.sql         # Database schema
└── README.md                  # Full documentation
```

---

**Your Smart Billing System is now running!** 🚀

Happy billing! If you have questions, refer to the full documentation in README.md
