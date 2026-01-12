// Mock API service for testing frontend without backend
// To use: import this instead of './api' in App.jsx

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const stockData = {
  AAPL: { name: 'Apple Inc.', price: 178.50 },
  TSLA: { name: 'Tesla Inc.', price: 242.75 },
  GOOGL: { name: 'Alphabet Inc.', price: 141.30 },
  MSFT: { name: 'Microsoft Corp.', price: 378.90 },
  AMZN: { name: 'Amazon.com Inc.', price: 152.25 },
  NVDA: { name: 'NVIDIA Corp.', price: 495.80 },
};

class MockApiService {
  async getPrediction(symbol) {
    await delay(1500); // Simulate API delay

    const stock = stockData[symbol] || { name: symbol, price: 100 };
    const changePercent = (Math.random() * 10 - 3).toFixed(2); // -3% to +7%
    const isPositive = parseFloat(changePercent) > 0;
    const currentPrice = stock.price;
    const predictedPrice = currentPrice * (1 + parseFloat(changePercent) / 100);
    const priceChange = predictedPrice - currentPrice;

    return {
      symbol,
      current_price: currentPrice,
      predicted_price: parseFloat(predictedPrice.toFixed(2)),
      price_change: parseFloat(priceChange.toFixed(2)),
      price_change_percent: parseFloat(changePercent),
      confidence_interval: {
        lower: parseFloat((predictedPrice * 0.97).toFixed(2)),
        upper: parseFloat((predictedPrice * 1.03).toFixed(2)),
      },
      model_confidence: parseFloat((0.75 + Math.random() * 0.2).toFixed(2)),
      prediction_date: new Date(Date.now() + 86400000).toISOString(), // Tomorrow
      direction: isPositive ? 'up' : 'down',
    };
  }

  async getSentiment(symbol) {
    await delay(1200); // Simulate API delay

    const sentimentOptions = [
      { score: 0.75, label: 'Positive', positive: 18, neutral: 5, negative: 2 },
      { score: 0.45, label: 'Neutral', positive: 8, neutral: 12, negative: 5 },
      { score: 0.25, label: 'Negative', positive: 3, neutral: 6, negative: 16 },
      { score: 0.85, label: 'Bullish', positive: 21, neutral: 3, negative: 1 },
    ];

    const sentiment = sentimentOptions[Math.floor(Math.random() * sentimentOptions.length)];
    const totalArticles = sentiment.positive + sentiment.neutral + sentiment.negative;

    return {
      symbol,
      sentiment_score: sentiment.score,
      sentiment_label: sentiment.label,
      article_count: totalArticles,
      positive_count: sentiment.positive,
      negative_count: sentiment.negative,
      neutral_count: sentiment.neutral,
      last_updated: new Date(Date.now() - Math.random() * 3600000).toISOString(), // Within last hour
    };
  }

  async getStocks() {
    await delay(500);
    return Object.keys(stockData).map(symbol => ({
      symbol,
      name: stockData[symbol].name,
    }));
  }

  async getHistoricalPrices(symbol, days = 30) {
    await delay(800);
    const prices = [];
    const basePrice = stockData[symbol]?.price || 100;
    
    for (let i = days; i >= 0; i--) {
      const date = new Date(Date.now() - i * 86400000);
      const randomChange = (Math.random() - 0.5) * 5;
      prices.push({
        date: date.toISOString().split('T')[0],
        close: parseFloat((basePrice + randomChange).toFixed(2)),
      });
    }
    
    return prices;
  }

  async getMetrics() {
    await delay(600);
    return {
      model_accuracy: 0.78,
      sentiment_accuracy: 0.85,
      total_predictions: 1247,
      avg_response_time_ms: 87,
    };
  }

  async healthCheck() {
    await delay(200);
    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
    };
  }
}

export default new MockApiService();
