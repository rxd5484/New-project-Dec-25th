# 🚀 QUICK DEPLOYMENT GUIDE - Get Your Demo Live in 10 Minutes

## Step-by-Step: Backend + Frontend Deployment (FREE)

### Part 1: Deploy Backend to Render.com (5 mins)

1. **Sign up at [render.com](https://render.com)** with GitHub

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo with backend code
   - Settings:
     - Name: `stock-ml-api` (or your choice)
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - Instance Type: Free
   
3. **Add MySQL Database** (if needed)
   - Click "New +" → "PostgreSQL" (or use external MySQL)
   - Note the connection URL
   - Add as environment variable in your web service

4. **Copy your API URL**
   - After deployment, copy the URL (e.g., `https://stock-ml-api.onrender.com`)
   - You'll need this for frontend!

### Part 2: Deploy Frontend to Vercel (2 mins)

1. **Push this frontend to GitHub**
```bash
cd stock-ml-frontend
git init
git add .
git commit -m "Add frontend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-ml-frontend.git
git push -u origin main
```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your GitHub repo
   - Framework Preset: Vite
   - Add Environment Variable:
     - Name: `VITE_API_URL`
     - Value: `https://stock-ml-api.onrender.com` (your backend URL from Part 1)
   - Click "Deploy"

3. **Done!** Your live demo URL: `https://your-project.vercel.app`

### Part 3: Update Your Resume (1 min)

Add to your project description:

```
Stock ML Pipeline | Python, PyTorch, FastAPI, React, MySQL
• Built ML system with LSTM + sentiment analysis achieving 78% directional accuracy
• Designed responsive React frontend with OpenAI-inspired UI/UX
• Deployed full-stack application with sub-100ms API response times
🔗 Live Demo: https://your-project.vercel.app
🔗 GitHub: https://github.com/YOUR_USERNAME/stock-ml-pipeline
```

---

## Alternative: Quick Test with Mock Data (Skip Backend)

If your backend isn't ready yet, you can still deploy the frontend with mock data:

1. **Create `src/services/mockApi.js`**
```javascript
export default {
  async getPrediction(symbol) {
    await new Promise(r => setTimeout(r, 1000)); // Simulate delay
    return {
      symbol,
      current_price: 150.25,
      predicted_price: 155.50,
      price_change: 5.25,
      price_change_percent: 3.49,
      confidence_interval: { lower: 152.00, upper: 159.00 },
      model_confidence: 0.87,
      prediction_date: new Date().toISOString(),
      direction: 'up'
    };
  },
  async getSentiment(symbol) {
    await new Promise(r => setTimeout(r, 1000));
    return {
      symbol,
      sentiment_score: 0.72,
      sentiment_label: 'Positive',
      article_count: 24,
      positive_count: 15,
      negative_count: 4,
      neutral_count: 5,
      last_updated: new Date().toISOString()
    };
  }
};
```

2. **Update `src/App.jsx`** - Replace:
```javascript
import api from './services/api';
```
with:
```javascript
import api from './services/mockApi'; // Use mock data
```

3. **Deploy to Vercel** (no backend needed!)

This lets you showcase the UI immediately while you finish the backend.

---

## Troubleshooting

**Backend won't start?**
- Check your `requirements.txt` includes all dependencies
- Verify `PORT` environment variable is used
- Check logs in Render dashboard

**Frontend shows errors?**
- Make sure `VITE_API_URL` is set correctly
- Check CORS is enabled on backend
- Open browser console for error messages

**API calls timeout?**
- Render free tier spins down after inactivity (takes ~1 min to wake up)
- First request might be slow, subsequent ones fast

---

## For Your Applications

When adding this to internship applications:

✅ **DO:**
- Include live demo link prominently
- Add screenshots/GIF of the interface
- Mention the tech stack
- Highlight the minimalistic design
- Link to GitHub repo

❌ **DON'T:**
- Just link to GitHub without demo
- Leave the default Vite page/styling
- Forget to test the demo before sending

**Pro tip**: Test your demo link in an incognito window before adding to applications. First impressions matter!

---

Need help? Check the main README.md for detailed documentation.
