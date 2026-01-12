# Deployment Guide - Railway + Vercel

Complete guide to deploy your Stock ML Pipeline to production.

## 🎯 Overview

**Backend**: Railway (Python + MySQL)
**Frontend**: Vercel (React/Vite)
**Total Time**: ~15 minutes
**Cost**: Free tier available

---

## 📋 Prerequisites

- GitHub account
- Railway account (free)
- Vercel account (free)
- Your code pushed to GitHub

---

## 🚀 Part 1: Backend Deployment (Railway)

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Authorize Railway

### Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Select your repository
4. Railway will detect Python automatically

### Step 3: Add MySQL Database

1. In your project, click "+ New"
2. Select "Database" → "MySQL"
3. Railway creates and connects database automatically

### Step 4: Configure Environment Variables

Railway auto-connects MySQL, but verify these are set:

```
MYSQLHOST=<automatically set>
MYSQLPORT=<automatically set>
MYSQLDATABASE=<automatically set>
MYSQLUSER=<automatically set>
MYSQLPASSWORD=<automatically set>
```

### Step 5: Initialize Database

Option A - Railway Console:
```bash
# In Railway dashboard, open shell and run:
python setup_complete.py
```

Option B - Local with Railway DB:
```bash
# Copy Railway MySQL credentials to local .env
python setup_complete.py
```

### Step 6: Deploy

Railway automatically:
- Installs from requirements.txt
- Runs the application
- Provides a public URL

Your backend will be at: `https://your-app.railway.app`

### Step 7: Test Deployment

```bash
# Test health
curl https://your-app.railway.app/health

# Test API
curl https://your-app.railway.app/stocks

# Check docs
open https://your-app.railway.app/docs
```

---

## 🎨 Part 2: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

Update `frontend/vite.config.js` to use environment variable:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
  },
  build: {
    outDir: 'dist',
  },
  // For production
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(
      process.env.VITE_API_URL || 'http://localhost:8000'
    ),
  },
})
```

### Step 2: Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Authorize Vercel

### Step 3: Import Project

1. Click "Add New Project"
2. Import your GitHub repository
3. Vercel auto-detects Vite

### Step 4: Configure Build Settings

Vercel should auto-detect:
- **Framework**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

If not, set these manually.

### Step 5: Set Environment Variables

In Vercel project settings → Environment Variables:

```
VITE_API_URL=https://your-app.railway.app
```

**Important**: Include full URL with https://

### Step 6: Deploy

Click "Deploy" and Vercel will:
- Install npm dependencies
- Build the project
- Deploy to CDN

Your frontend will be at: `https://your-app.vercel.app`

### Step 7: Test Deployment

1. Open your Vercel URL
2. Try searching for a stock (AAPL, TSLA, etc.)
3. Verify predictions and sentiment display
4. Check browser console for errors

---

## 🔧 Configuration Files

### Railway

Create `railway.json` in project root (optional):

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python src/api/main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `Procfile` for Gunicorn (optional, better for production):

```
web: gunicorn src.api.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

Then add to requirements.txt:
```
gunicorn
```

### Vercel

Create `vercel.json` in frontend directory (optional):

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "installCommand": "npm install",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## 🔐 Security Configuration

### Production CORS (Backend)

Update `src/api/main.py`:

```python
# Replace this:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# With this:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # ✅ Your frontend
        "https://your-custom-domain.com",  # ✅ Custom domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # ✅ Specific methods
    allow_headers=["Content-Type"],  # ✅ Specific headers
)
```

### Environment Variables Security

**Never commit:**
- .env files
- Database credentials
- API keys

**Use:**
- Railway environment variables
- Vercel environment variables
- GitHub Secrets for CI/CD

---

## 📊 Monitoring & Logs

### Railway Logs

```bash
# View logs in Railway dashboard
# Or use Railway CLI:
railway logs
```

### Vercel Logs

```bash
# View in Vercel dashboard
# Or use Vercel CLI:
vercel logs
```

### Custom Logging

Add to `src/api/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

---

## 🚀 Performance Optimization

### Backend

1. **Add Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_stock_data(symbol: str):
    # Cache results for 5 minutes
    pass
```

2. **Database Connection Pooling**:
Already configured in `db_manager.py`

3. **Compression**:
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Frontend

1. **Code Splitting**: Already handled by Vite
2. **Image Optimization**: Use WebP format
3. **Lazy Loading**: 
```javascript
const Component = lazy(() => import('./Component'))
```

---

## 🔄 Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

---

## 🌐 Custom Domain

### Railway

1. Go to project settings
2. Click "Settings" → "Domains"
3. Add custom domain
4. Update DNS records as shown

### Vercel

1. Go to project settings
2. Click "Domains"
3. Add custom domain
4. Vercel provides DNS instructions

Update CORS in backend after adding domain!

---

## 🐛 Troubleshooting Deployment

### Railway Issues

**Build fails:**
- Check Railway logs
- Verify requirements.txt is complete
- Test locally with: `pip install -r requirements.txt`

**Database connection fails:**
- Check environment variables are set
- Verify MySQL service is running
- Test with: `railway run python -c "from src.database.db_manager import get_db_manager; get_db_manager().test_connection()"`

**App crashes:**
- Check logs: `railway logs`
- Verify port binding: Use `0.0.0.0:$PORT`
- Check for uncaught exceptions

### Vercel Issues

**Build fails:**
- Check build logs in Vercel dashboard
- Verify frontend dependencies: `cd frontend && npm install`
- Test local build: `npm run build`

**API calls fail:**
- Verify VITE_API_URL is set correctly
- Check CORS on backend
- Open browser console for errors

**Blank page:**
- Check for JavaScript errors
- Verify build output directory
- Check routing configuration

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to GitHub
- [ ] Database schema is finalized
- [ ] Environment variables documented
- [ ] All dependencies in requirements.txt/package.json
- [ ] Tested locally

### Railway (Backend)
- [ ] Project created
- [ ] MySQL database added
- [ ] Environment variables set
- [ ] Database initialized with data
- [ ] Health endpoint responds
- [ ] API docs accessible at /docs

### Vercel (Frontend)
- [ ] Project imported
- [ ] Build settings configured
- [ ] VITE_API_URL environment variable set
- [ ] Build succeeds
- [ ] Site loads correctly
- [ ] API calls work

### Post-Deployment
- [ ] Update CORS to use specific origins
- [ ] Test all features
- [ ] Monitor logs for errors
- [ ] Set up alerts
- [ ] Document deployment process
- [ ] Update README with live URLs

---

## 🎯 Production URLs

After deployment, update these in documentation:

- **Backend API**: `https://your-app.railway.app`
- **Frontend**: `https://your-app.vercel.app`
- **API Docs**: `https://your-app.railway.app/docs`

Test commands:
```bash
# Backend health
curl https://your-app.railway.app/health

# Frontend
open https://your-app.vercel.app
```

---

## 💰 Cost Estimation

### Free Tier Limits

**Railway**:
- $5 free credit per month
- Enough for small-medium traffic
- MySQL included

**Vercel**:
- 100 GB bandwidth/month
- Unlimited builds and deployments
- Edge network included

**Both are free for hobby/learning projects!**

---

## 🎉 You're Live!

Your Stock ML Pipeline is now deployed and accessible worldwide! 🚀

**Next steps:**
1. Share your live URLs
2. Monitor usage and logs
3. Iterate based on feedback
4. Add real ML models
5. Scale as needed

---

## 📞 Support

**Railway**: [railway.app/help](https://railway.app/help)
**Vercel**: [vercel.com/support](https://vercel.com/support)

---

**Deployment complete!** Your app is now running in production. 🎊
