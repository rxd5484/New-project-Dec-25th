import { useState } from 'react'
import { Search, ArrowRight } from 'lucide-react'
import { getStockPrediction, getStockSentiment } from '../services/api'

const POPULAR_STOCKS = ['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL', 'MSFT']

export default function StockSearch({ onSearch, loading }) {
  const [symbol, setSymbol] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!symbol.trim()) return

    try {
      const [prediction, sentiment] = await Promise.all([
        getStockPrediction(symbol.toUpperCase()),
        getStockSentiment(symbol.toUpperCase())
      ])
      onSearch({ prediction, sentiment })
    } catch (error) {
      console.error('Error fetching data:', error)
      throw error
    }
  }

  const handleQuickSelect = async (stock) => {
    setSymbol(stock)
    try {
      const [prediction, sentiment] = await Promise.all([
        getStockPrediction(stock),
        getStockSentiment(stock)
      ])
      onSearch({ prediction, sentiment })
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  return (
    <div className="space-y-4">
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center gap-3 bg-zinc-900 border-2 border-zinc-800 rounded-2xl px-6 py-4 focus-within:border-blue-500 transition-all">
          <Search className="w-5 h-5 text-zinc-500" />
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter stock symbol (e.g., AAPL, TSLA)"
            className="flex-1 bg-transparent text-lg outline-none placeholder-zinc-600"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !symbol.trim()}
            className="px-6 py-2.5 bg-white text-black rounded-xl font-semibold hover:bg-zinc-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                Predict
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>

      {/* Quick Select */}
      <div className="flex items-center gap-3 justify-center flex-wrap">
        <span className="text-sm text-zinc-500">Popular:</span>
        {POPULAR_STOCKS.map((stock) => (
          <button
            key={stock}
            onClick={() => handleQuickSelect(stock)}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 hover:border-zinc-700 transition-colors disabled:opacity-50"
          >
            {stock}
          </button>
        ))}
      </div>
    </div>
  )
}
