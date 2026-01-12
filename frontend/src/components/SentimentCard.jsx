import { MessageSquare, ThumbsUp, ThumbsDown, Minus, Newspaper } from 'lucide-react';

function SentimentCard({ sentiment }) {
  const { 
    symbol, 
    sentiment_score, 
    sentiment_label,
    article_count,
    positive_count,
    negative_count,
    neutral_count,
    last_updated 
  } = sentiment;

  const getSentimentColor = (label) => {
    switch (label.toLowerCase()) {
      case 'positive':
      case 'bullish':
        return {
          bg: 'bg-emerald-50',
          border: 'border-emerald-200',
          text: 'text-emerald-700',
          badge: 'badge-success',
          icon: ThumbsUp,
        };
      case 'negative':
      case 'bearish':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-700',
          badge: 'badge-danger',
          icon: ThumbsDown,
        };
      default:
        return {
          bg: 'bg-slate-50',
          border: 'border-slate-200',
          text: 'text-slate-700',
          badge: 'badge-neutral',
          icon: Minus,
        };
    }
  };

  const sentimentStyle = getSentimentColor(sentiment_label);
  const SentimentIcon = sentimentStyle.icon;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const calculatePercentage = (count, total) => {
    return total > 0 ? ((count / total) * 100).toFixed(1) : '0.0';
  };

  return (
    <div className="card p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-bold text-slate-800 mb-1">Sentiment Analysis</h3>
          <div className="text-sm text-slate-500">Market sentiment for {symbol}</div>
        </div>
        <div className={`${sentimentStyle.bg} ${sentimentStyle.border} border rounded-xl px-3 py-2`}>
          <MessageSquare className={`w-6 h-6 ${sentimentStyle.text}`} />
        </div>
      </div>

      {/* Sentiment score */}
      <div className="bg-gradient-to-br from-slate-50 to-blue-50/50 rounded-xl p-6 border border-slate-200/60">
        <div className="text-sm text-slate-600 mb-3 font-medium">Overall Sentiment</div>
        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1">
            <div className="flex items-end gap-2 mb-2">
              <div className="text-3xl font-bold text-slate-900">
                {(sentiment_score * 100).toFixed(1)}
              </div>
              <div className="text-slate-500 mb-1">/ 100</div>
            </div>
            <div className={`${sentimentStyle.badge} inline-flex items-center gap-1.5`}>
              <SentimentIcon className="w-3.5 h-3.5" />
              <span className="font-semibold">{sentiment_label}</span>
            </div>
          </div>
          
          {/* Sentiment bar */}
          <div className="flex-1">
            <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
              <div 
                className={`h-full ${
                  sentiment_label.toLowerCase() === 'positive' || sentiment_label.toLowerCase() === 'bullish'
                    ? 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                    : sentiment_label.toLowerCase() === 'negative' || sentiment_label.toLowerCase() === 'bearish'
                    ? 'bg-gradient-to-r from-red-500 to-red-600'
                    : 'bg-gradient-to-r from-slate-400 to-slate-500'
                }`}
                style={{ width: `${Math.abs(sentiment_score) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Article breakdown */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-slate-600 font-medium">
          <Newspaper className="w-4 h-4" />
          <span>Analyzed {article_count} recent articles</span>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="metric-card">
            <div className="flex items-center gap-1.5 mb-2">
              <ThumbsUp className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-xs text-slate-600 font-medium">Positive</span>
            </div>
            <div className="text-lg font-bold text-slate-900">{positive_count}</div>
            <div className="text-xs text-slate-500 mt-1">
              {calculatePercentage(positive_count, article_count)}%
            </div>
          </div>

          <div className="metric-card">
            <div className="flex items-center gap-1.5 mb-2">
              <Minus className="w-3.5 h-3.5 text-slate-600" />
              <span className="text-xs text-slate-600 font-medium">Neutral</span>
            </div>
            <div className="text-lg font-bold text-slate-900">{neutral_count}</div>
            <div className="text-xs text-slate-500 mt-1">
              {calculatePercentage(neutral_count, article_count)}%
            </div>
          </div>

          <div className="metric-card">
            <div className="flex items-center gap-1.5 mb-2">
              <ThumbsDown className="w-3.5 h-3.5 text-red-600" />
              <span className="text-xs text-slate-600 font-medium">Negative</span>
            </div>
            <div className="text-lg font-bold text-slate-900">{negative_count}</div>
            <div className="text-xs text-slate-500 mt-1">
              {calculatePercentage(negative_count, article_count)}%
            </div>
          </div>
        </div>
      </div>

      {/* Last updated */}
      {last_updated && (
        <div className="pt-4 border-t border-slate-200 text-xs text-slate-500">
          Last updated: {formatDate(last_updated)}
        </div>
      )}
    </div>
  );
}

export default SentimentCard;
