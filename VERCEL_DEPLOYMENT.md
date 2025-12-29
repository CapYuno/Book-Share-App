# Deploying BookShare to Vercel

This guide explains how to deploy the BookShare Flask application to Vercel's serverless platform.

## ⚠️ Important Limitations

Before deploying to Vercel, understand these critical limitations:

### 1. **Database Requirements**
- ❌ SQLite will **NOT work** on Vercel (serverless functions are stateless)
- ✅ You **MUST** use a hosted PostgreSQL database
- Recommended options:
  - [Supabase](https://supabase.com) (Free tier available)
  - [Neon](https://neon.tech) (Free tier available)
  - [Railway](https://railway.app) (Free tier available)
  - [Render PostgreSQL](https://render.com)

### 2. **Scheduler Limitations**
- ❌ APScheduler (email reminders) will **NOT work** on Vercel
- The scheduler has been disabled for Vercel deployments
- Alternatives:
  - Use [Vercel Cron Jobs](https://vercel.com/docs/cron-jobs) (Pro plan required)
  - Use external cron service (e.g., cron-job.org)
  - Implement reminders client-side or via webhooks

### 3. **Timeout Constraints**
- Hobby Plan: **10-second timeout** per function
- Pro Plan: **60-second timeout** per function (configured in `vercel.json`)
- Long-running operations may fail

### 4. **File Storage**
- ❌ Local file storage doesn't persist between requests
- If you generate files (like `tfidf_cache.pkl`), they won't persist
- Consider using cloud storage or rebuilding cache per request

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Hosted Database**: Set up a PostgreSQL database (see options above)
3. **Vercel CLI** (optional): `npm install -g vercel`
4. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Set Up Database

### Using Supabase (Recommended)

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the database to provision
3. Go to **Project Settings** → **Database**
4. Copy the **Connection String** (URI format)
5. It should look like: `postgresql://postgres:[password]@[host]:5432/postgres`

### Using Neon

1. Go to [neon.tech](https://neon.tech) and create a new project
2. Copy the connection string from the dashboard
3. It should look like: `postgresql://[user]:[password]@[host]/[database]`

## Step 2: Configure Environment Variables

You'll need to set these environment variables in Vercel:

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Flask
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=BookShare <noreply@bookshare.com>
```

### Optional Variables

```bash
# Reminder Settings
REMINDER_BEFORE_DUE=3
REMINDER_AFTER_DUE=3

# Recommendation Settings
RECOMMENDATIONS_TOP_K=3
TF_IDF_MIN_DF=2
TF_IDF_MAX_FEATURES=1000
TF_IDF_NGRAM_RANGE=1,2

# Performance
MAX_SEARCH_RESULTS=100
```

## Step 3: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Easiest)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click **Import Project**
   - Select your GitHub repository
   - Vercel will auto-detect the configuration from `vercel.json`

3. **Configure Environment Variables**
   - In the import screen, click **Environment Variables**
   - Add all required variables from Step 2
   - Click **Deploy**

4. **Wait for deployment**
   - Vercel will build and deploy your application
   - You'll get a URL like `your-app.vercel.app`

### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd /path/to/bookshare
   vercel
   ```

4. **Follow the prompts**
   - Link to existing project or create new one
   - Set environment variables when prompted
   - Deploy to production: `vercel --prod`

## Step 4: Initialize Database

After deployment, you need to initialize your database tables:

### Option 1: Using Flask CLI (If accessible)

If you can run commands on Vercel (via Vercel CLI):

```bash
vercel env pull .env.local  # Download environment variables
flask db upgrade            # Run migrations (if using Flask-Migrate)
flask seed-db              # Seed database (if you have this command)
```

### Option 2: Manual SQL Execution

1. Connect to your database using a client (pgAdmin, TablePlus, or psql)
2. Run the schema creation SQL manually
3. Insert seed data if needed

### Option 3: Temporary Route (Quick & Dirty)

Add a temporary route to initialize the database:

```python
# In app/__init__.py, add after registering blueprints:
@app.route('/init-db-secret-route')
def init_db():
    db.create_all()
    return "Database initialized!"
```

Visit `your-app.vercel.app/init-db-secret-route` once, then remove the route.

## Step 5: Verify Deployment

Test your deployment:

1. **Homepage**: Visit `your-app.vercel.app`
2. **Books List**: Visit `your-app.vercel.app/books`
3. **Dashboard**: Visit `your-app.vercel.app/dashboard`
4. **Test CRUD Operations**: Create, read, update, delete books/borrowers/loans

## Troubleshooting

### Problem: "Internal Server Error" (500)

**Solution**: Check Vercel logs
```bash
vercel logs
```

Common causes:
- Missing environment variables
- Database connection issues
- Module import errors

### Problem: "Function execution timed out"

**Solution**: 
- Optimize slow database queries
- Reduce data processing
- Consider upgrading to Vercel Pro for 60s timeout

### Problem: Database connection failed

**Solution**:
- Verify `DATABASE_URL` is correct
- Check database allows connections from Vercel's IP ranges
- Test connection string locally first

### Problem: Static files not loading

**Solution**:
- Check `vercel.json` static file routing
- Ensure files are in `app/static/` directory
- Verify `.vercelignore` isn't excluding static files

### Problem: ImportError or ModuleNotFoundError

**Solution**:
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility
- Review Vercel build logs for errors

## Known Issues & Workarounds

### Email Reminders Don't Work

**Issue**: APScheduler is disabled on Vercel

**Workarounds**:
1. Use Vercel Cron Jobs (Pro plan):
   ```json
   // vercel.json
   {
     "crons": [{
       "path": "/api/send-reminders",
       "schedule": "0 9 * * *"
     }]
   }
   ```

2. Use an external cron service to hit an endpoint
3. Implement client-side notifications

### Recommendation Cache Not Persisting

**Issue**: `tfidf_cache.pkl` doesn't persist between requests

**Workarounds**:
1. Store cache in database as a BLOB
2. Use cloud storage (S3, Cloudinary)
3. Rebuild cache on each request (may be slow)
4. Use a caching service (Redis, Memcached)

## Performance Tips

1. **Database Indexing**: Add indexes to frequently queried columns
2. **Connection Pooling**: Use `psycopg2` connection pooling
3. **Query Optimization**: Use eager loading to reduce N+1 queries
4. **Caching**: Implement Redis for frequently accessed data
5. **CDN**: Use Vercel's CDN for static assets

## Cost Considerations

**Vercel Hobby Plan (Free)**:
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ⚠️ 10-second function timeout
- ❌ No cron jobs

**Vercel Pro Plan ($20/month)**:
- ✅ 60-second function timeout
- ✅ Cron jobs
- ✅ 1 TB bandwidth/month
- ✅ Team collaboration

## Alternative: Stick with Render

If these limitations are too restrictive, **Render is a better choice** for BookShare:
- ✅ No timeout issues
- ✅ Persistent processes
- ✅ Background jobs work
- ✅ Better for traditional Flask apps

Your app is already configured for Render - see `RENDER_DEPLOYMENT.md`

## Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Support**: [vercel.com/support](https://vercel.com/support)
- **BookShare Issues**: Open an issue on your GitHub repository

---

**Good luck with your deployment!** 🚀
