# Render Deployment - Quick Start

## 🚀 Deploy in 5 Minutes

### Prerequisites
- GitHub repository pushed (see `PUSH_TO_GITHUB.md`)
- Render account (free tier available)

### Step 1: Connect Repository

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect GitHub account (if not already)
4. Select repository: `Athrv-DxT/Genuine-Bazaar_Team-cracked`
5. Click **"Apply"**

### Step 2: Configure Services

Render will automatically detect `render.yaml` and create:
- ✅ PostgreSQL Database (`retail-cortex-db`)
- ✅ Web Service (`retail-cortex-api`)

### Step 3: Set Environment Variables

After services are created, go to each service and add:

**Web Service Environment Variables:**
```
OPENWEATHER_API_KEY=your_openweather_api_key
CALENDARIFIC_API_KEY=your_calendarific_api_key
TWITTER_BEARER_TOKEN=your_twitter_token (optional)
DEBUG=False
CORS_ORIGINS=*
```

**Note**: `DATABASE_URL` and `SECRET_KEY` are auto-configured by Render.

### Step 4: Deploy

1. Click **"Apply"** on the Blueprint
2. Wait for deployment (5-10 minutes)
3. Check logs for any errors

### Step 5: Initialize Database

After first deployment:

1. Go to Web Service → **"Shell"** tab
2. Run:
   ```bash
   python init_db.py
   ```

### Step 6: Test Deployment

1. Check health endpoint:
   ```
   https://your-app-name.onrender.com/health
   ```

2. Check API docs:
   ```
   https://your-app-name.onrender.com/docs
   ```

## 🔧 Manual Setup (Alternative)

If Blueprint doesn't work:

### Create Database

1. **New** → **PostgreSQL**
2. Name: `retail-cortex-db`
3. Plan: Free
4. Copy **Internal Database URL**

### Create Web Service

1. **New** → **Web Service**
2. Connect GitHub repository
3. Settings:
   - **Name**: `retail-cortex-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app`
   - **Plan**: Free

4. **Environment Variables**:
   ```
   DATABASE_URL=<Internal Database URL from PostgreSQL>
   SECRET_KEY=<Generate random string>
   OPENWEATHER_API_KEY=<Your key>
   CALENDARIFIC_API_KEY=<Your key>
   DEBUG=False
   CORS_ORIGINS=*
   ```

## 📝 Post-Deployment

### Verify Everything Works

- [ ] Health check returns `{"status": "healthy"}`
- [ ] API docs accessible at `/docs`
- [ ] Database initialized (no errors in logs)
- [ ] Can register/login users
- [ ] Trends page loads

### Frontend Deployment (Optional)

Deploy frontend as separate Static Site:

1. **New** → **Static Site**
2. Connect same repository
3. Settings:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Environment**: `Node`

## 🐛 Troubleshooting

### Build Fails
- Check Python version (3.11+)
- Verify `requirements.txt` is correct
- Check build logs for errors

### Database Connection Error
- Use **Internal Database URL** (not External)
- Check `DATABASE_URL` format
- Ensure database service is running

### API Not Responding
- Check start command in service settings
- Verify `PORT` environment variable
- Review application logs

### 500 Errors
- Check application logs
- Verify all environment variables set
- Ensure database is initialized

## 📚 Additional Resources

- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Project README: See `README.md`

## 🎉 Success!

Once deployed, your API will be available at:
```
https://your-app-name.onrender.com
```

API Documentation:
```
https://your-app-name.onrender.com/docs
```

