import { useState } from 'react'
import StockSearch from './components/StockSearch'
import PredictionCard from './components/PredictionCard'
import SentimentCard from './components/SentimentCard'
import { TrendingUp } from 'lucide-react'

function App() {
  const [stockData, setStockData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (data) => {
    setLoading(true)
    setError(null)
    try {
      setStockData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="border-b border-zinc-800">
        <div className="max-w-2xl mx-auto px-4 py-3">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-5 h-5 text-blue-500" />
            <h1 className="text-base font-semibold">Stock Analysis</h1>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-4">
        {/* Search */}
        <StockSearch onSearch={handleSearch} loading={loading} />

        {/* Error */}
        {error && (
          <div className="mt-3 p-3 bg-red-950/30 border border-red-900/50 rounded-lg">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Results */}
        {stockData && !loading && (
          <div className="space-y-3 mt-3">
            <PredictionCard data={stockData.prediction} />
            <SentimentCard data={stockData.sentiment} />
          </div>
        )}

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-zinc-800">
          <p className="text-xs text-zinc-600 text-center">
            Powered by LSTM + Sentiment Analysis
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
