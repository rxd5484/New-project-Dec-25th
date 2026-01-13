import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

export default function PredictionCard({ data }) {
  if (!data) return null

  const { 
    symbol, 
    current_price, 
    predicted_price, 
    price_change, 
    price_change_percent,
    model_confidence,
    direction 
  } = data

  const isUp = direction === 'up'
  const isDown = direction === 'down'

  return (
    <div className="border-2 border-zinc-800 rounded-2xl p-8 bg-zinc-900/30 hover:border-zinc-700 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-2">Price Prediction</h3>
          <p className="text-4xl font-bold">{symbol}</p>
        </div>
        <div className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold ${
          isUp ? 'bg-green-950/30 text-green-400 border border-green-900' :
          isDown ? 'bg-red-950/30 text-red-400 border border-red-900' :
          'bg-zinc-800 text-zinc-400 border border-zinc-700'
        }`}>
          {isUp && <TrendingUp className="w-4 h-4" />}
          {isDown && <TrendingDown className="w-4 h-4" />}
          {!isUp && !isDown && <Minus className="w-4 h-4" />}
          {price_change_percent > 0 && '+'}{price_change_percent.toFixed(2)}%
        </div>
      </div>

      {/* Prices */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div>
          <p className="text-sm text-zinc-500 mb-2">Current Price</p>
          <p className="text-3xl font-bold">${current_price.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-zinc-500 mb-2">Predicted Price</p>
          <p className="text-3xl font-bold">${predicted_price.toFixed(2)}</p>
        </div>
      </div>

      {/* Confidence */}
      <div className="pt-6 border-t-2 border-zinc-800">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-zinc-400 font-medium">Model Confidence</span>
          <span className="text-lg font-bold">{(model_confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-500"
            style={{ width: `${model_confidence * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}
