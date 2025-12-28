# RENDER IS STUCK ON PYTHON 3.13 - HERE'S THE FIX

## The Problem
Render Blueprint cached Python 3.13 when you first created the service.
NO amount of config changes will fix a Blueprint that's already created.

## THE SOLUTION (Delete & Recreate - 5 Minutes)

### Step 1: Delete Current Service
1. Go to Render Dashboard
2. Find your `bookshare` service
3. Click **Settings** (bottom left)
4. Scroll down → Click **"Delete Web Service"**
5. Type the service name to confirm

### Step 2: Create NEW Web Service (NOT Blueprint!)
1. Click **"New +"** → **"Web Service"** (NOT Blueprint!)
2. Connect to GitHub: `Book-Share-App`
3. Configure:
   - **Name**: `bookshare` (or whatever you want)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```
     pip install --upgrade pip && pip install -r requirements.txt && flask init-db && flask seed-db --books 50 --borrowers 10 --loans 20 && flask rebuild-recs
     ```
   - **Start Command**: 
     ```
     gunicorn run:app --bind 0.0.0.0:$PORT
     ```
   - **Instance Type**: `Free`

### Step 3: Add Environment Variables
Click **"Advanced"** → Add these:

```
PYTHON_VERSION = 3.11.9
FLASK_ENV = production  
SECRET_KEY = [click "Generate" button]
```

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes
3. Python 3.11.9 will be used
4. scikit-learn will install from wheel (no compilation)
5. **SUCCESS!** ✅

---

## Why This Works
- **Manual Web Service** respects PYTHON_VERSION environment variable
- **Blueprint** was caching the old Python version
- Fresh service = fresh Python version

## Your App Will Be At:
`https://bookshare-xxxx.onrender.com`

---

## If You Want to Keep It Simple (Alternative)

Skip scikit-learn entirely and use a simpler recommendation system:

1. I can remove scikit-learn from requirements
2. Replace with basic keyword/genre matching
3. Deploys instantly, no Python version issues
4. Still has recommendations, just simpler algorithm

**Let me know which approach you prefer:**
- ✅ Delete & recreate service (recommended, keeps AI features)
- ⚡ Remove scikit-learn, use simpler recommendations (faster deploy)
