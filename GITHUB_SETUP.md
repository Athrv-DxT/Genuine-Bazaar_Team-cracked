# GitHub Setup Instructions

## Quick Start - Push to GitHub

Since Git might not be installed, follow these steps:

### Option 1: Using GitHub Desktop (Easiest)

1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in with your GitHub account
3. Click "File" → "Add Local Repository"
4. Select the `C:\Genuine-Bazaar` folder
5. Click "Publish repository" → Select `Athrv-DxT/Genuine-Bazaar_Team-cracked`
6. Click "Publish repository"

### Option 2: Using Git Command Line

1. **Install Git** (if not installed):
   - Download from: https://git-scm.com/download/win
   - Install with default settings

2. **Open PowerShell/Command Prompt** in the project folder:
   ```powershell
   cd C:\Genuine-Bazaar
   ```

3. **Initialize Git**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Retail Cortex platform"
   ```

4. **Add Remote and Push**:
   ```bash
   git remote add origin https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked.git
   git branch -M main
   git push -u origin main
   ```

### Option 3: Using GitHub Web Interface

1. Go to: https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked
2. Click "uploading an existing file"
3. Drag and drop all files (except node_modules, venv, .env, *.db)
4. Commit changes

## Files to Include

✅ **Include these files:**
- All Python files (`app/`, `*.py`)
- Frontend source (`frontend/src/`)
- Configuration files (`requirements.txt`, `Procfile`, `render.yaml`, `runtime.txt`)
- Documentation (`README.md`, `DEPLOYMENT.md`)
- `.gitignore`

❌ **Don't include:**
- `venv/` or `env/` (virtual environment)
- `frontend/node_modules/`
- `.env` files
- `*.db` files (database files)
- `__pycache__/` folders
- `instance/` folder

## After Pushing

Once pushed to GitHub:

1. Go to Render Dashboard
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml` and deploy

## Repository Structure

```
Genuine-Bazaar/
├── app/                    # Backend application
│   ├── main.py            # FastAPI app
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   ├── routes/            # API routes
│   ├── services/          # Business logic
│   ├── models/            # Database models
│   └── schemas/           # Pydantic schemas
├── frontend/               # React frontend
│   ├── src/               # Source files
│   ├── package.json       # Dependencies
│   └── vite.config.js     # Vite config
├── requirements.txt        # Python dependencies
├── Procfile               # Process file for Render
├── render.yaml            # Render deployment config
├── runtime.txt            # Python version
├── init_db.py             # Database initialization
├── start_all.py           # Local development script
├── README.md              # Project documentation
└── DEPLOYMENT.md          # Deployment guide
```

