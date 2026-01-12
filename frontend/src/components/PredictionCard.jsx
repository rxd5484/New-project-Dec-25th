import { TrendingUp, TrendingDown, DollarSign, Target, Clock } from 'lucide-react';

function PredictionCard({ prediction }) {
  const { 
    symbol, 
    current_price, 
    predicted_price, 
    price_change, 
    price_change_percent,
    confidence_interval,
    model_confidence,
    prediction_date,
    direction 
  } = prediction;

  const isPositive = price_change > 0;
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;
  const trendColor = isPositive ? 'text-emerald-600' : 'text-red-600';
  const bgColor = isPositive ? 'bg-emerald-50' : 'bg-red-50';
  const borderColor = isPositive ? 'border-emerald-200' : 'border-red-200';

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const formatPercent = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="card p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-800 mb-1">{symbol}</h2>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Clock className="w-4 h-4" />
            <span>Prediction for {formatDate(prediction_date)}</span>
          </div>
        </div>
        <div className={`${bgColor} ${borderColor} border rounded-xl px-3 py-2`}>
          <TrendIcon className={`w-6 h-6 ${trendColor}`} />
        </div>
      </div>

      {/* Main prediction */}
      <div className="bg-gradient-to-br from-slate-50 to-blue-50/50 rounded-xl p-6 border border-slate-200/60">
        <div className="text-sm text-slate-600 mb-2 font-medium">Predicted Price</div>
        <div className="flex items-end gap-3 mb-4">
          <div className="text-4xl font-bold text-slate-900">
            {formatPrice(predicted_price)}
          </div>
          <div className={`${trendColor} font-semibold text-lg mb-1`}>
            {formatPercent(price_change_percent)}
          </div>
        </div>
        
        <div className="flex items-center gap-2 text-sm">
          <span className="text-slate-500">Current:</span>
          <span className="font-semibold text-slate-700">{formatPrice(current_price)}</span>
          <span className="text-slate-400">•</span>
          <span className="text-slate-500">Change:</span>
          <span className={`font-semibold ${trendColor}`}>
            {formatPrice(Math.abs(price_change))}
          </span>
        </div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="metric-card">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-blue-600" />
            <span className="text-xs text-slate-600 font-medium">Direction</span>
          </div>
          <div className={`badge ${isPositive ? 'badge-success' : 'badge-danger'}`}>
            {direction.toUpperCase()}
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-4 h-4 text-blue-600" />
            <span className="text-xs text-slate-600 font-medium">Confidence</span>
          </div>
          <div className="text-lg font-bold text-slate-900">
            {(model_confidence * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Confidence interval */}
      {confidence_interval && (
        <div className="pt-4 border-t border-slate-200">
          <div className="text-xs text-slate-600 mb-3 font-medium">Confidence Interval (95%)</div>
          <div className="flex items-center justify-between text-sm">
            <div>
              <span className="text-slate-500">Low:</span>
              <span className="ml-2 font-semibold text-slate-700">
                {formatPrice(confidence_interval.lower)}
              </span>
            </div>
            <div>
              <span className="text-slate-500">High:</span>
              <span className="ml-2 font-semibold text-slate-700">
                {formatPrice(confidence_interval.upper)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PredictionCard;
