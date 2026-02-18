# Smart Billing System - Deployment Guide

## Deploying on Vercel (Frontend)

### Step 1: Create GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/Smart_Billing_System.git
git push -u origin main
```

### Step 2: Deploy Frontend to Vercel
1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Select `frontend` as the root directory
5. Add environment variables:
   - `REACT_APP_API_URL`: Your backend URL
   - `REACT_APP_SUPABASE_URL`: Your Supabase URL
   - `REACT_APP_SUPABASE_ANON_KEY`: Your Supabase Key
6. Click Deploy

## Deploying Backend on Railway

### Step 1: Push to GitHub (if not already done)
```bash
git push origin main
```

### Step 2: Deploy Backend to Railway
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Choose your repository
5. Select the `backend` directory
6. Add environment variables in Railway dashboard:
   - `PORT`: 5000
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `NODE_ENV`: production
7. Watch the deployment logs

### Step 3: Get Backend URL
After deployment, Railway will provide a public URL. Update your frontend's `REACT_APP_API_URL` environment variable with this URL.

## Deploying on Heroku (Alternative)

### Step 1: Install Heroku CLI
```bash
# On macOS
brew tap heroku/brew && brew install heroku

# On Windows (using npm)
npm install -g heroku
```

### Step 2: Create Heroku App
```bash
heroku login
cd backend
heroku create your-app-name
```

### Step 3: Set Environment Variables
```bash
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_ANON_KEY=your_key
heroku config:set NODE_ENV=production
```

### Step 4: Deploy
```bash
git push heroku main
```

## Using Docker Locally

### Build Docker Images
```bash
docker-compose build
```

### Run with Docker Compose
```bash
docker-compose up
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Environment Variables for Production

### Backend
```
PORT=5000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
NODE_ENV=production
```

### Frontend
```
REACT_APP_API_URL=https://your-backend-url.com
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_anon_key
```

## Domain Configuration

### Using Custom Domain with Vercel (Frontend)
1. In Vercel dashboard, go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as per Vercel instructions

### Using Custom Domain with Railway (Backend)
1. In Railway dashboard, go to Networking
2. Add your custom domain
3. Configure DNS settings

## SSL/HTTPS
Both Vercel and Railway provide free SSL certificates automatically.

## Monitoring & Logs

### Railway Logs
```bash
railway logs -f
```

### Heroku Logs
```bash
heroku logs --tail
```

### Vercel Analytics
Available in Vercel dashboard under Analytics tab.

## Troubleshooting Deployment

### Frontend won't load
- Check REACT_APP_API_URL is correct
- Verify backend is running and accessible
- Check browser console for CORS errors

### Backend API calls failing
- Verify Supabase credentials are correct
- Check Supabase project is active
- Review backend logs for errors

### Database issues
- Verify Supabase database tables exist
- Run database_setup.sql if needed
- Check row-level security policies

## Performance Optimization

### Frontend
- Code splitting enabled by default in React
- Vercel CDN caches static assets
- Image optimization available

### Backend
- Database indexes created for better performance
- Consider caching frequently accessed data
- Monitor API response times

## Backup & Recovery

### Supabase Database Backups
1. Go to Supabase dashboard
2. Project Settings → Backups
3. Manual backups available with paid plans
4. Automatic backups every 24 hours

### Code Backups
GitHub automatically backs up your code. Configure branch protection rules for safety.
