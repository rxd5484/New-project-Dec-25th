# Stock ML Pipeline - Frontend

A clean, minimalistic React frontend for the Stock ML Pipeline. Features AI-powered stock predictions and sentiment analysis with a sleek OpenAI-inspired UI.

## 🎨 Features

- **Real-time Stock Analysis**: Search any stock ticker for instant predictions
- **Sentiment Analysis**: View market sentiment from recent news articles
- **Clean UI**: Minimalistic design with smooth animations
- **Responsive**: Works seamlessly on desktop and mobile
- **Fast**: Optimized for performance with <100ms API response times

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Your Stock ML backend running (default: `http://localhost:8000`)

### Installation

1. **Clone or download this project**
```bash
cd stock-ml-frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and set VITE_API_URL to your backend URL
```

4. **Start development server**
```bash
npm run dev
```

Visit `http://localhost:3000` to see your app!

## 📦 Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` folder ready for deployment.

## 🌐 Deployment Guide

### Option 1: Deploy to Vercel (Recommended - Free)

1. **Push your code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your GitHub repository
   - Add environment variable:
     - Name: `VITE_API_URL`
     - Value: Your backend API URL (e.g., `https://your-api.render.com`)
   - Click "Deploy"

Your frontend will be live in ~2 minutes! 🎉

### Option 2: Deploy to Netlify (Free)

1. **Build the project**
```bash
npm run build
```

2. **Deploy**
   - Go to [netlify.com](https://www.netlify.com/)
   - Drag & drop the `dist/` folder
   - Or connect your GitHub repo for automatic deployments

3. **Set environment variables** in Netlify dashboard:
   - `VITE_API_URL` = Your backend URL

### Option 3: Deploy to Render (Free)

1. **Push to GitHub** (same as Vercel step 1)

2. **Create new Static Site on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Static Site"
   - Connect your GitHub repository
   - Settings:
     - Build Command: `npm install && npm run build`
     - Publish Directory: `dist`
   - Add environment variable: `VITE_API_URL`
   - Click "Create Static Site"

## 🔧 Project Structure

```
stock-ml-frontend/
├── src/
│   ├── components/
│   │   ├── StockSearch.jsx      # Search input component
│   │   ├── PredictionCard.jsx   # Displays prediction results
│   │   └── SentimentCard.jsx    # Shows sentiment analysis
│   ├── services/
│   │   └── api.js               # API communication layer
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── public/                      # Static assets
├── index.html                   # HTML template
├── package.json                 # Dependencies
├── vite.config.js              # Vite configuration
└── tailwind.config.js          # Tailwind CSS config
```

## 🎨 Customization

### Update Colors
Edit `tailwind.config.js` to change the color scheme:
```js
colors: {
  primary: {
    500: '#your-color',
    600: '#your-darker-color',
  },
}
```

### Update Fonts
Edit `index.html` to change fonts (line 12-14):
```html
<link href="https://fonts.googleapis.com/css2?family=YourFont:wght@400;700&display=swap">
```

Then update `tailwind.config.js`:
```js
fontFamily: {
  sans: ['YourFont', 'sans-serif'],
}
```

## 🔌 API Endpoints Expected

Your backend should implement these endpoints:

- `GET /stocks` - List available stocks
- `GET /predict/{symbol}` - Get prediction for a stock
- `GET /sentiment/{symbol}` - Get sentiment analysis
- `GET /stocks/{symbol}/prices` - Get historical prices
- `GET /health` - Health check

Expected response formats are in `src/services/api.js`.

## 📝 Environment Variables

- `VITE_API_URL` - Your backend API URL (required)

## 🛠️ Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool (super fast!)
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Recharts** - Charts (optional, for future enhancements)

## 📸 Screenshots

[Add screenshots of your deployed app here]

## 🤝 Contributing

Feel free to customize and extend this frontend for your needs!

## 📄 License

MIT

## 💡 Tips for Your Resume/Portfolio

When showcasing this project:

1. **Link to live demo** - "Live Demo: [your-vercel-url]"
2. **Highlight the tech stack** - React, Vite, Tailwind, API integration
3. **Mention the minimalistic design** - "OpenAI-inspired UI/UX"
4. **Add metrics** - "Sub-100ms API response times"
5. **Include a screenshot** - Visual is worth 1000 words

Example resume bullet:
> "Built responsive React frontend with OpenAI-inspired minimalistic design, integrating ML prediction API with <100ms response times; deployed on Vercel with CI/CD"

---

Built with ❤️ for showcasing ML engineering skills
