"""
Unit Tests for Stock ML Pipeline
Demonstrates testing best practices for ML projects
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from database.db_manager import DatabaseManager
from data_collection.collect_data import StockDataCollector
from models.train_predictor import AttentionLSTM


class TestDatabaseManager:
    """Test database operations."""
    
    def test_database_connection(self):
        """Test database connection."""
        db = DatabaseManager()
        assert db.test_connection() == True
    
    def test_get_stock_id(self):
        """Test retrieving stock ID."""
        db = DatabaseManager()
        stock_id = db.get_stock_id('AAPL')
        assert stock_id is not None
        assert isinstance(stock_id, int)
    
    def test_fetch_dict(self):
        """Test fetching data as dictionary."""
        db = DatabaseManager()
        stocks = db.fetch_dict("SELECT * FROM stocks LIMIT 1")
        assert len(stocks) > 0
        assert 'symbol' in stocks[0]
        assert 'company_name' in stocks[0]


class TestStockDataCollector:
    """Test data collection functionality."""
    
    def test_calculate_technical_indicators(self):
        """Test technical indicator calculations."""
        # Create sample data
        dates = pd.date_range(start='2023-01-01', periods=100)
        data = {
            'Date': dates,
            'Close': np.random.randn(100).cumsum() + 100,
            'Open': np.random.randn(100).cumsum() + 100,
            'High': np.random.randn(100).cumsum() + 102,
            'Low': np.random.randn(100).cumsum() + 98,
            'Volume': np.random.randint(1000000, 10000000, 100)
        }
        df = pd.DataFrame(data)
        
        collector = StockDataCollector()
        df_with_indicators = collector.calculate_technical_indicators(df)
        
        # Check indicators were calculated
        assert 'sma_20' in df_with_indicators.columns
        assert 'ema_12' in df_with_indicators.columns
        assert 'rsi' in df_with_indicators.columns
        assert 'macd' in df_with_indicators.columns
        
        # Check RSI is in valid range (0-100)
        rsi_values = df_with_indicators['rsi'].dropna()
        assert (rsi_values >= 0).all()
        assert (rsi_values <= 100).all()


class TestAttentionLSTM:
    """Test LSTM model architecture."""
    
    def test_model_initialization(self):
        """Test model can be initialized."""
        model = AttentionLSTM(
            input_size=13,
            hidden_size=64,
            num_layers=2,
            dropout=0.2
        )
        assert model is not None
    
    def test_forward_pass(self):
        """Test model forward pass."""
        import torch
        
        model = AttentionLSTM(
            input_size=13,
            hidden_size=64,
            num_layers=2,
            dropout=0.2
        )
        
        # Create dummy input (batch_size=4, seq_len=60, features=13)
        x = torch.randn(4, 60, 13)
        
        # Forward pass
        output = model(x)
        
        # Check output shape (batch_size, 1)
        assert output.shape == (4, 1)
    
    def test_model_parameters(self):
        """Test model has trainable parameters."""
        model = AttentionLSTM(input_size=13, hidden_size=64)
        
        # Count parameters
        num_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        assert num_params > 0


class TestDataValidation:
    """Test data validation and quality checks."""
    
    def test_price_data_completeness(self):
        """Test that price data doesn't have missing required fields."""
        db = DatabaseManager()
        
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN close_price IS NULL THEN 1 ELSE 0 END) as missing_close,
                SUM(CASE WHEN volume IS NULL THEN 1 ELSE 0 END) as missing_volume
            FROM stock_prices
            WHERE price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """
        
        result = db.fetch_dict(query)
        
        if result and result[0]['total'] > 0:
            assert result[0]['missing_close'] == 0, "Found NULL close prices"
            assert result[0]['missing_volume'] == 0, "Found NULL volumes"
    
    def test_no_duplicate_prices(self):
        """Test that there are no duplicate price entries."""
        db = DatabaseManager()
        
        query = """
            SELECT stock_id, price_date, COUNT(*) as count
            FROM stock_prices
            GROUP BY stock_id, price_date
            HAVING COUNT(*) > 1
        """
        
        duplicates = db.fetch_dict(query)
        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate entries"
    
    def test_price_data_chronological(self):
        """Test that price data is stored chronologically."""
        db = DatabaseManager()
        
        query = """
            SELECT price_date
            FROM stock_prices
            WHERE stock_id = (SELECT stock_id FROM stocks LIMIT 1)
            ORDER BY price_date
            LIMIT 100
        """
        
        dates = db.execute_query(query)
        
        if len(dates) > 1:
            # Check dates are in ascending order
            for i in range(len(dates) - 1):
                assert dates[i][0] <= dates[i+1][0], "Dates not in chronological order"


class TestPredictionValidation:
    """Test prediction outputs are valid."""
    
    def test_prediction_in_reasonable_range(self):
        """Test predictions are within reasonable bounds."""
        db = DatabaseManager()
        
        # Get recent predictions
        query = """
            SELECT predicted_price, actual_price, confidence_lower, confidence_upper
            FROM predictions
            WHERE actual_price IS NOT NULL
            LIMIT 10
        """
        
        predictions = db.fetch_dict(query)
        
        for pred in predictions:
            # Prediction should be positive
            assert pred['predicted_price'] > 0, "Negative price prediction"
            
            # Confidence interval should contain prediction
            assert pred['confidence_lower'] <= pred['predicted_price'] <= pred['confidence_upper'], \
                "Prediction outside confidence interval"
            
            # If actual price exists, check it's positive
            if pred['actual_price']:
                assert pred['actual_price'] > 0, "Negative actual price"


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from api.main import app
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_get_stocks(self, client):
        """Test getting stock list."""
        response = client.get("/stocks")
        assert response.status_code == 200
        stocks = response.json()
        assert len(stocks) > 0
        assert 'symbol' in stocks[0]
    
    def test_get_stock_prices(self, client):
        """Test getting stock prices."""
        response = client.get("/stocks/AAPL/prices?days=30")
        
        if response.status_code == 200:
            prices = response.json()
            assert len(prices) > 0
            assert 'close_price' in prices[0]
            assert 'date' in prices[0]


# Performance benchmarks
class TestPerformance:
    """Performance and efficiency tests."""
    
    def test_database_query_performance(self):
        """Test that database queries execute quickly."""
        import time
        
        db = DatabaseManager()
        
        # Time a simple query
        start = time.time()
        db.fetch_dict("SELECT * FROM stocks")
        duration = time.time() - start
        
        # Should complete in under 1 second
        assert duration < 1.0, f"Query took {duration:.2f}s, expected < 1s"
    
    def test_model_inference_speed(self):
        """Test that model inference is fast enough."""
        import time
        import torch
        
        model = AttentionLSTM(input_size=13, hidden_size=64)
        model.eval()
        
        # Create dummy input
        x = torch.randn(1, 60, 13)
        
        # Warm up
        with torch.no_grad():
            _ = model(x)
        
        # Time inference
        start = time.time()
        with torch.no_grad():
            for _ in range(100):
                _ = model(x)
        duration = time.time() - start
        
        # Should average < 10ms per inference
        avg_time = duration / 100
        assert avg_time < 0.01, f"Inference took {avg_time*1000:.2f}ms, expected < 10ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])