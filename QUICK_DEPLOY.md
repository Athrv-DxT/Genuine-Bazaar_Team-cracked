# 🚀 Quick Deploy Guide

## Step 1: Push to GitHub (Choose One Method)

### Option A: GitHub Desktop (Easiest)
1. Download: https://desktop.github.com/
2. File → Add Local Repository → Select `C:\Genuine-Bazaar`
3. Commit → Publish → Select `Athrv-DxT/Genuine-Bazaar_Team-cracked`

### Option B: Command Line
```bash
cd C:\Genuine-Bazaar
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect GitHub → Select repository
4. Click **"Apply"** (Render auto-detects `render.yaml`)
5. Add environment variables:
   - `OPENWEATHER_API_KEY` = Your key
   - `CALENDARIFIC_API_KEY` = Your key
6. Wait for deployment (5-10 min)

## Step 3: Initialize Database

After deployment:
1. Web Service → **"Shell"** tab
2. Run: `python init_db.py`

## ✅ Done!

Your API will be live at:
```
https://your-app-name.onrender.com
```

API Docs:
```
https://your-app-name.onrender.com/docs
```

## 📚 Full Guides

- **GitHub Setup**: See `PUSH_TO_GITHUB.md`
- **Render Deployment**: See `RENDER_DEPLOY.md`
- **Full Documentation**: See `DEPLOYMENT.md`

