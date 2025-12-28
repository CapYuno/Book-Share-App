# Render Deployment Quick Start

## ✅ Files Created & Pushed to GitHub

- ✅ `render.yaml` - Automatic deployment configuration
- ✅ `build.sh` - Build script with database initialization
- ✅ `RENDER_DEPLOYMENT.md` - Complete deployment guide
- ✅ `requirements.txt` - Updated with gunicorn & PostgreSQL

## 🚀 Deploy Now (5 Minutes)

### Step 1: Go to Render
1. Visit [render.com](https://render.com)
2. Sign up/login with your GitHub account

### Step 2: Create New Blueprint
1. Click **"New +"** → **"Blueprint"**
2. Select your repository: **Book-Share-App**
3. Render will detect `render.yaml` automatically
4. Click **"Apply"**

### Step 3: Wait for Deployment
- Build takes ~5-10 minutes
- Watch the logs for progress
- Sample data (100 books, 20 borrowers) will be auto-loaded

### Step 4: Access Your Live App
Your app will be at: `https://bookshare-xxxx.onrender.com`

## 🎯 What Happens Automatically

✅ Python 3.11 environment  
✅ All dependencies installed (including scikit-learn)  
✅ Database created and initialized  
✅ Sample data seeded  
✅ AI recommendation cache built  
✅ App deployed and running  

## ⚙️ Optional: Email Reminders

Add these environment variables in Render dashboard:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📚 Full Guide

See `RENDER_DEPLOYMENT.md` for detailed instructions and troubleshooting.

## 🔄 Future Updates

Just push to GitHub:
```bash
git push origin main
```
Render automatically redeploys!
