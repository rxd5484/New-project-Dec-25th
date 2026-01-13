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
    <div className="border border-zinc-800 rounded-xl p-4 bg-zinc-900/50">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-zinc-400">Price Prediction</h3>
          <p className="text-2xl font-bold mt-1">{symbol}</p>
        </div>
        <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
          isUp ? 'bg-green-950/30 text-green-400' :
          isDown ? 'bg-red-950/30 text-red-400' :
          'bg-zinc-800 text-zinc-400'
        }`}>
          {isUp && <TrendingUp className="w-3 h-3" />}
          {isDown && <TrendingDown className="w-3 h-3" />}
          {!isUp && !isDown && <Minus className="w-3 h-3" />}
          {price_change_percent > 0 && '+'}{price_change_percent.toFixed(2)}%
        </div>
      </div>

      {/* Prices */}
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <p className="text-xs text-zinc-500">Current</p>
          <p className="text-lg font-semibold">${current_price.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs text-zinc-500">Predicted</p>
          <p className="text-lg font-semibold">${predicted_price.toFixed(2)}</p>
        </div>
      </div>

      {/* Confidence */}
      <div className="pt-3 border-t border-zinc-800">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500">Model Confidence</span>
          <span className="font-medium">{(model_confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="mt-1.5 h-1 bg-zinc-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-500 rounded-full"
            style={{ width: `${model_confidence * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}
