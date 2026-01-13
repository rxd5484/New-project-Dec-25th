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
    <div className="border border-zinc-800 rounded-xl p-4 bg-zinc-900/50">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-zinc-400">Market Sentiment</h3>
          <p className="text-2xl font-bold mt-1">{(sentiment_score * 100).toFixed(0)}</p>
        </div>
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
          sentiment_label === 'Positive' ? 'bg-green-950/30 text-green-400' :
          sentiment_label === 'Negative' ? 'bg-red-950/30 text-red-400' :
          'bg-zinc-800 text-zinc-400'
        }`}>
          {sentiment_label}
        </div>
      </div>

      {/* Bar Chart */}
      <div className="space-y-2 mb-3">
        <div className="flex items-center gap-2">
          <ThumbsUp className="w-3 h-3 text-green-400" />
          <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-green-500 rounded-full"
              style={{ width: `${positivePercent}%` }}
            />
          </div>
          <span className="text-xs text-zinc-500 w-8 text-right">{positive_count}</span>
        </div>

        <div className="flex items-center gap-2">
          <Minus className="w-3 h-3 text-zinc-400" />
          <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-zinc-500 rounded-full"
              style={{ width: `${neutralPercent}%` }}
            />
          </div>
          <span className="text-xs text-zinc-500 w-8 text-right">{neutral_count}</span>
        </div>

        <div className="flex items-center gap-2">
          <ThumbsDown className="w-3 h-3 text-red-400" />
          <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-red-500 rounded-full"
              style={{ width: `${negativePercent}%` }}
            />
          </div>
          <span className="text-xs text-zinc-500 w-8 text-right">{negative_count}</span>
        </div>
      </div>

      {/* Total */}
      <div className="pt-3 border-t border-zinc-800 flex items-center gap-2 text-xs text-zinc-500">
        <MessageCircle className="w-3 h-3" />
        <span>{article_count} articles analyzed</span>
      </div>
    </div>
  )
}
