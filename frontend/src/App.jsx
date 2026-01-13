import { useState } from 'react'
import StockSearch from './components/StockSearch'
import PredictionCard from './components/PredictionCard'
import SentimentCard from './components/SentimentCard'
import { TrendingUp, BarChart3, Brain, Zap } from 'lucide-react'

function App() {
  const [stockData, setStockData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showResults, setShowResults] = useState(false)

  const handleSearch = async (data) => {
    setLoading(true)
    setError(null)
    try {
      setStockData(data)
      setShowResults(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleBackToSearch = () => {
    setShowResults(false)
    setStockData(null)
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {!showResults ? (
        // Hero Landing Page
        <div className="flex flex-col items-center justify-center min-h-screen px-4">
          {/* Logo/Brand */}
          <div className="mb-12 flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-blue-500" />
            <span className="text-xl font-semibold">StockML</span>
          </div>

          {/* Hero Text */}
          <div className="text-center max-w-5xl mx-auto mb-16">
            <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold mb-8 leading-tight">
              AI-Powered Stock
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
                Price Prediction
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-zinc-400 max-w-3xl mx-auto">
              LSTM neural networks combined with sentiment analysis to predict next-day stock movements with confidence intervals.
            </p>
          </div>

          {/* CTA Search */}
          <div className="w-full max-w-2xl mb-16">
            <StockSearch onSearch={handleSearch} loading={loading} />
            {error && (
              <div className="mt-4 p-4 bg-red-950/30 border border-red-900/50 rounded-xl">
                <p className="text-sm text-red-400 text-center">{error}</p>
              </div>
            )}
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
            <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/30 hover:border-zinc-700 transition-colors">
              <Brain className="w-8 h-8 text-blue-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">LSTM Neural Network</h3>
              <p className="text-sm text-zinc-500">Attention-based architecture trained on 2 years of historical data</p>
            </div>
            
            <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/30 hover:border-zinc-700 transition-colors">
              <BarChart3 className="w-8 h-8 text-purple-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Sentiment Analysis</h3>
              <p className="text-sm text-zinc-500">Real-time market sentiment from news articles and social media</p>
            </div>
            
            <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/30 hover:border-zinc-700 transition-colors">
              <Zap className="w-8 h-8 text-green-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">54.5% Accuracy</h3>
              <p className="text-sm text-zinc-500">Directional accuracy on validation set with confidence intervals</p>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-16 pt-8 border-t border-zinc-900 w-full max-w-4xl">
            <p className="text-xs text-zinc-600 text-center">
              Built with PyTorch, FastAPI, React · Deployed on Railway & Vercel
            </p>
          </div>
        </div>
      ) : (
        // Results Page
        <div className="min-h-screen">
          {/* Header */}
          <div className="border-b border-zinc-800 sticky top-0 bg-black/80 backdrop-blur-sm z-10">
            <div className="max-w-4xl mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <button 
                  onClick={handleBackToSearch}
                  className="flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back to search
                </button>
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-blue-500" />
                  <span className="text-base font-semibold">StockML</span>
                </div>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="space-y-6">
              <PredictionCard data={stockData?.prediction} />
              <SentimentCard data={stockData?.sentiment} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
