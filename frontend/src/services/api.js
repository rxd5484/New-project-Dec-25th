const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  async fetchWithTimeout(url, options = {}, timeout = 10000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      clearTimeout(id);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  async getStocks() {
    return this.fetchWithTimeout(`${API_BASE_URL}/stocks`);
  }

  async getPrediction(symbol) {
    return this.fetchWithTimeout(`${API_BASE_URL}/predict/${symbol}`);
  }

  async getSentiment(symbol) {
    return this.fetchWithTimeout(`${API_BASE_URL}/sentiment/${symbol}`);
  }

  async getHistoricalPrices(symbol, days = 30) {
    return this.fetchWithTimeout(`${API_BASE_URL}/stocks/${symbol}/prices?days=${days}`);
  }

  async getMetrics() {
    return this.fetchWithTimeout(`${API_BASE_URL}/metrics`);
  }

  async healthCheck() {
    return this.fetchWithTimeout(`${API_BASE_URL}/health`);
  }
}

export default new ApiService();
