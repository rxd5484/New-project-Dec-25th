import { useState } from 'react'
import { Search } from 'lucide-react'
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
    <div className="space-y-3">
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-full px-4 py-2.5 focus-within:border-blue-500 transition-colors">
          <Search className="w-4 h-4 text-zinc-500" />
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Search stocks..."
            className="flex-1 bg-transparent text-sm outline-none placeholder-zinc-600"
            disabled={loading}
          />
          {loading && (
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          )}
        </div>
      </form>

      {/* Quick Select */}
      <div className="flex flex-wrap gap-2">
        {POPULAR_STOCKS.map((stock) => (
          <button
            key={stock}
            onClick={() => handleQuickSelect(stock)}
            disabled={loading}
            className="px-3 py-1.5 text-xs font-medium bg-zinc-900 border border-zinc-800 rounded-full hover:bg-zinc-800 hover:border-zinc-700 transition-colors disabled:opacity-50"
          >
            {stock}
          </button>
        ))}
      </div>
    </div>
  )
}
