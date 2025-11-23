# Deployment Guide for Retail Cortex

## Deploying to Render

### Prerequisites
1. GitHub account
2. Render account (sign up at https://render.com)

### Step 1: Push to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Retail Cortex platform"
   ```

2. **Add Remote Repository**:
   ```bash
   git remote add origin https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked.git
   git branch -M main
   ```

3. **Push to GitHub**:
   ```bash
   git push -u origin main
   ```

### Step 2: Deploy on Render

#### Option A: Using render.yaml (Recommended)

1. Go to https://dashboard.render.com
2. Click "New" → "Blueprint"
3. Connect your GitHub repository: `Athrv-DxT/Genuine-Bazaar_Team-cracked`
4. Render will automatically detect `render.yaml` and create:
   - Web service (API)
   - PostgreSQL database

#### Option B: Manual Setup

1. **Create PostgreSQL Database**:
   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - Name: `retail-cortex-db`
   - Plan: Free (or paid)
   - Copy the **Internal Database URL**

2. **Create Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Name**: `retail-cortex-api`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app`
     - **Plan**: Free (or paid)

3. **Set Environment Variables**:
   - `DATABASE_URL`: (from PostgreSQL service - Internal Database URL)
   - `SECRET_KEY`: (Generate a random string)
   - `OPENWEATHER_API_KEY`: (Your OpenWeatherMap API key)
   - `CALENDARIFIC_API_KEY`: (Your Calendarific API key)
   - `TWITTER_BEARER_TOKEN`: (Optional - for social media trends)
   - `DEBUG`: `False`
   - `CORS_ORIGINS`: `*` (or your frontend URL)

4. **Deploy Frontend** (Optional - separate service):
   - Click "New" → "Static Site"
   - Connect repository
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`

### Step 3: Initialize Database

After deployment, run database migrations:

1. Go to your web service on Render
2. Open "Shell" tab
3. Run:
   ```bash
   python init_db.py
   ```

### Environment Variables Reference

```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API Keys
OPENWEATHER_API_KEY=your-openweather-api-key
CALENDARIFIC_API_KEY=your-calendarific-api-key
TWITTER_BEARER_TOKEN=your-twitter-bearer-token

# Settings
DEBUG=False
CORS_ORIGINS=*
```

### Post-Deployment Checklist

- [ ] Database initialized
- [ ] Environment variables set
- [ ] API health check: `https://your-app.onrender.com/health`
- [ ] Frontend deployed (if separate)
- [ ] CORS configured correctly
- [ ] Background jobs running (scheduler)

### Troubleshooting

**Database Connection Issues**:
- Use Internal Database URL (not External)
- Check DATABASE_URL format
- Ensure database is running

**Build Failures**:
- Check Python version (3.11+)
- Verify all dependencies in requirements.txt
- Check build logs

**API Not Responding**:
- Check start command
- Verify PORT environment variable
- Review application logs

### Support

For issues, check:
- Render logs: Dashboard → Your Service → Logs
- Application logs: Check FastAPI logs
- Database logs: PostgreSQL service logs
