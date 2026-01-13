const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function getStockPrediction(symbol) {
  const response = await fetch(`${API_URL}/predict/${symbol}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch prediction for ${symbol}`)
  }
  return response.json()
}

export async function getStockSentiment(symbol) {
  const response = await fetch(`${API_URL}/sentiment/${symbol}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch sentiment for ${symbol}`)
  }
  return response.json()
}

export async function getAvailableStocks() {
  const response = await fetch(`${API_URL}/stocks`)
  if (!response.ok) {
    throw new Error('Failed to fetch available stocks')
  }
  return response.json()
}

export async function getHealthCheck() {
  const response = await fetch(`${API_URL}/health`)
  if (!response.ok) {
    throw new Error('API health check failed')
  }
  return response.json()
}
