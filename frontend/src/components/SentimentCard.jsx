import { MessageCircle, ThumbsUp, ThumbsDown, Minus } from 'lucide-react'

export default function SentimentCard({ data }) {
  if (!data) return null

  const {
    symbol,
    sentiment_label,
    sentiment_score,
    positive_count,
    negative_count,
    neutral_count,
    article_count
  } = data

  const positivePercent = (positive_count / article_count) * 100
  const negativePercent = (negative_count / article_count) * 100
  const neutralPercent = (neutral_count / article_count) * 100

  return (
    <div className="border-2 border-zinc-800 rounded-2xl p-8 bg-zinc-900/30 hover:border-zinc-700 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-2">Market Sentiment</h3>
          <p className="text-4xl font-bold">{(sentiment_score * 100).toFixed(0)}</p>
        </div>
        <div className={`px-4 py-2 rounded-xl text-sm font-semibold border ${
          sentiment_label === 'Positive' ? 'bg-green-950/30 text-green-400 border-green-900' :
          sentiment_label === 'Negative' ? 'bg-red-950/30 text-red-400 border-red-900' :
          'bg-zinc-800 text-zinc-400 border-zinc-700'
        }`}>
          {sentiment_label}
        </div>
      </div>

      {/* Bar Chart */}
      <div className="space-y-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 w-20">
            <ThumbsUp className="w-4 h-4 text-green-400" />
            <span className="text-sm font-medium text-green-400">{positive_count}</span>
          </div>
          <div className="flex-1 h-3 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full transition-all duration-500"
              style={{ width: `${positivePercent}%` }}
            />
          </div>
          <span className="text-xs text-zinc-500 w-12 text-right">{positivePercent.toFixed(0)}%</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 w-20">
            <Minus className="w-4 h-4 text-zinc-400" />
            <span className="text-sm font-medium text-zinc-400">{neutral_count}</span>
          </div>
          <div className="flex-1 h-3 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-zinc-500 rounded-full transition-all duration-500"
              style={{ width: `${neutralPercent}%` }}
            />
          </div>
          <span className="text-xs text-zinc-500 w-12 text-right">{neutralPercent.toFixed(0)}%</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 w-20">
            <ThumbsDown className="w-4 h-4 text-red-400" />
            <span className="text-sm font-medium text-red-400">{negative_count}</span>
          </div>
          <div className="flex-1 h-3 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-red-500 to-red-400 rounded-full transition-all duration-500"
              style={{ width: `${negativePercent}%` }}
            />
          </div>
          <span className="text-xs text-zinc-500 w-12 text-right">{negativePercent.toFixed(0)}%</span>
        </div>
      </div>

      {/* Total */}
      <div className="pt-6 border-t-2 border-zinc-800 flex items-center gap-3 text-sm text-zinc-400">
        <MessageCircle className="w-4 h-4" />
        <span className="font-medium">{article_count} articles analyzed</span>
      </div>
    </div>
  )
}
