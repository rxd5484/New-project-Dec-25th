import { useState } from 'react';
import { TrendingUp, Activity, Brain, Sparkles } from 'lucide-react';
import StockSearch from './components/StockSearch';
import PredictionCard from './components/PredictionCard';
import SentimentCard from './components/SentimentCard';
import api from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (symbol) => {
    setLoading(true);
    setError(null);
    setPrediction(null);
    setSentiment(null);

    try {
      const [predictionData, sentimentData] = await Promise.all([
        api.getPrediction(symbol),
        api.getSentiment(symbol),
      ]);

      setPrediction(predictionData);
      setSentiment(sentimentData);
    } catch (err) {
      setError(err.message || 'Failed to fetch data. Please try again.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-cyan-400/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
      </div>

      {/* Main content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="pt-16 pb-12 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 bg-blue-100/80 backdrop-blur-sm text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6 animate-fade-in">
              <Sparkles className="w-4 h-4" />
              <span>ML-Powered Stock Intelligence</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold mb-4 animate-fade-in">
              <span className="text-gradient">Stock Market</span>
              <br />
              <span className="text-slate-800">Predictions</span>
            </h1>
            
            <p className="text-slate-600 text-lg max-w-2xl mx-auto animate-fade-in" style={{ animationDelay: '0.1s' }}>
              Advanced LSTM models combined with sentiment analysis to predict stock movements
            </p>
          </div>
        </header>

        {/* Search Section */}
        <main className="px-4 pb-20">
          <div className="max-w-4xl mx-auto space-y-8">
            <StockSearch onSearch={handleSearch} loading={loading} />

            {error && (
              <div className="card p-6 border-red-200 bg-red-50/50 animate-slide-up">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                    <Activity className="w-5 h-5 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {loading && (
              <div className="space-y-6 animate-slide-up">
                <div className="card p-8">
                  <div className="flex items-center justify-center gap-3 mb-4">
                    <Brain className="w-6 h-6 text-blue-600 animate-pulse" />
                    <span className="text-slate-600 font-medium">Analyzing market data...</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-blue-600 to-cyan-600 loading-shimmer" />
                  </div>
                </div>
              </div>
            )}

            {!loading && prediction && (
              <div className="grid md:grid-cols-2 gap-6 animate-slide-up">
                <PredictionCard prediction={prediction} />
                {sentiment && <SentimentCard sentiment={sentiment} />}
              </div>
            )}

            {!loading && !prediction && !error && (
              <div className="card p-12 text-center animate-slide-up">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-100 to-cyan-100 rounded-2xl flex items-center justify-center">
                  <TrendingUp className="w-10 h-10 text-blue-600" />
                </div>
                <h3 className="text-2xl font-bold text-slate-800 mb-2">Get Started</h3>
                <p className="text-slate-600 max-w-md mx-auto">
                  Enter a stock ticker symbol above to view AI-powered predictions and sentiment analysis
                </p>
              </div>
            )}
          </div>
        </main>

        {/* Footer */}
        <footer className="py-8 px-4 border-t border-slate-200/60">
          <div className="max-w-4xl mx-auto text-center text-slate-500 text-sm">
            <p>
              Built with PyTorch, FastAPI, and React • Powered by LSTM + Sentiment Analysis
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
