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
          <div className="mb-16 flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-blue-500" />
            <span className="text-xl font-semibold">StockML</span>
          </div>

          {/* Hero Text - OpenAI Style */}
          <div className="text-center max-w-6xl mx-auto mb-16">
            <h1 className="text-7xl md:text-8xl lg:text-9xl font-bold mb-8 leading-none tracking-tight">
              Stock Price
            </h1>
            <p className="text-2xl md:text-3xl text-zinc-400 font-light max-w-4xl mx-auto leading-relaxed">
              Machine learning models that predict tomorrow's market movements.
            </p>
          </div>

          {/* CTA Search */}
          <div className="w-full max-w-2xl mb-20">
            <StockSearch onSearch={handleSearch} loading={loading} />
            {error && (
              <div className="mt-4 p-4 bg-red-950/30 border border-red-900/50 rounded-xl">
                <p className="text-sm text-red-400 text-center">{error}</p>
              </div>
            )}
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl w-full mb-16">
            <div className="p-8 rounded-2xl border border-zinc-800 bg-zinc-900/30 hover:border-zinc-700 transition-all">
              <Brain className="w-10 h-10 text-blue-500 mb-4" />
              <h3 className="text-xl font-semibold mb-3">LSTM Networks</h3>
              <p className="text-base text-zinc-500 leading-relaxed">
                Attention-based architecture trained on 2 years of historical data with technical indicators.
              </p>
            </div>
            
            <div className="p-8 rounded-2xl border border-zinc-800 bg-zinc-900/30 hover:border-zinc-700 transition-all">
              <BarChart3 className="w-10 h-10 text-purple-500 mb-4" />
              <h3 className="text-xl font-semibold mb-3">Sentiment Analysis</h3>
              <p className="text-base text-zinc-500 leading-relaxed">
                Real-time market sentiment extracted from news articles and social media feeds.
              </p>
            </div>
            
            <div className="p-8 rounded-2xl border border-zinc-800 bg-zinc-900/30 hover:border-zinc-700 transition-all">
              <Zap className="w-10 h-10 text-green-500 mb-4" />
              <h3 className="text-xl font-semibold mb-3">Confidence Intervals</h3>
              <p className="text-base text-zinc-500 leading-relaxed">
                Predictions include confidence intervals and directional accuracy metrics.
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="pt-8 border-t border-zinc-900 w-full max-w-5xl">
            <p className="text-sm text-zinc-600 text-center font-light">
              Built with PyTorch, FastAPI, and React · Deployed on Railway & Vercel
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
