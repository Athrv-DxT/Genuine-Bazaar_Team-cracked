# Quick Guide: Push to GitHub

## Step-by-Step Instructions

### Method 1: GitHub Desktop (Recommended for Windows)

1. **Download GitHub Desktop**: https://desktop.github.com/
2. **Install and Login** with your GitHub account
3. **Add Repository**:
   - File → Add Local Repository
   - Browse to: `C:\Genuine-Bazaar`
   - Click "Add repository"
4. **Commit Files**:
   - Review changes
   - Write commit message: "Initial commit - Retail Cortex platform"
   - Click "Commit to main"
5. **Publish**:
   - Click "Publish repository"
   - Repository name: `Genuine-Bazaar_Team-cracked`
   - Owner: `Athrv-DxT`
   - Make sure "Keep this code private" is UNCHECKED (if you want it public)
   - Click "Publish repository"

### Method 2: Command Line (If Git is Installed)

Open PowerShell in `C:\Genuine-Bazaar` and run:

```powershell
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Retail Cortex platform"

# Add remote
git remote add origin https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked.git

# Push
git branch -M main
git push -u origin main
```

### Method 3: VS Code (If You Use VS Code)

1. Open VS Code in `C:\Genuine-Bazaar`
2. Click Source Control icon (left sidebar)
3. Click "Initialize Repository"
4. Stage all files (click + next to "Changes")
5. Commit: "Initial commit - Retail Cortex platform"
6. Click "..." → "Remote" → "Add Remote"
7. Name: `origin`, URL: `https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked.git`
8. Click "..." → "Push" → "Push to..."

## Important Notes

⚠️ **Before pushing, make sure:**
- `.env` file is NOT included (it's in .gitignore)
- Database files (`*.db`) are NOT included
- `venv/` folder is NOT included
- `node_modules/` is NOT included

✅ **Files that SHOULD be pushed:**
- All Python code (`app/` folder)
- Frontend code (`frontend/src/`)
- Configuration files (`requirements.txt`, `Procfile`, `render.yaml`)
- Documentation files
- `.gitignore`

## After Pushing

1. Verify on GitHub: https://github.com/Athrv-DxT/Genuine-Bazaar_Team-cracked
2. Go to Render Dashboard
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will auto-deploy!

## Troubleshooting

**"Repository not found"**:
- Check repository name: `Genuine-Bazaar_Team-cracked`
- Verify you have access to `Athrv-DxT` organization

**"Authentication failed"**:
- Use GitHub Desktop (easiest)
- Or set up SSH keys
- Or use Personal Access Token

**"Large file" error**:
- Remove `venv/` folder
- Remove `node_modules/` folder
- Remove `*.db` files
- These are in `.gitignore` already

