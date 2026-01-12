import { useState } from 'react';
import { Search, TrendingUp } from 'lucide-react';

const popularStocks = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA'];

function StockSearch({ onSearch, loading }) {
  const [symbol, setSymbol] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (symbol.trim() && !loading) {
      onSearch(symbol.trim().toUpperCase());
    }
  };

  const handleQuickSelect = (stock) => {
    setSymbol(stock);
    onSearch(stock);
  };

  return (
    <div className="card p-8 animate-slide-up">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
            <Search className="w-5 h-5" />
          </div>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter stock ticker (e.g., AAPL, TSLA)"
            className="input-field w-full pl-12 text-lg"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !symbol.trim()}
          className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <TrendingUp className="w-5 h-5" />
          <span>{loading ? 'Analyzing...' : 'Analyze Stock'}</span>
        </button>
      </form>

      <div className="mt-6 pt-6 border-t border-slate-200">
        <p className="text-sm text-slate-500 mb-3 font-medium">Popular stocks:</p>
        <div className="flex flex-wrap gap-2">
          {popularStocks.map((stock) => (
            <button
              key={stock}
              onClick={() => handleQuickSelect(stock)}
              disabled={loading}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm font-medium text-slate-700 transition-all duration-200 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {stock}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default StockSearch;
