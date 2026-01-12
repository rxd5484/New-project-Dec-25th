"""
Data Collection Module
Fetches stock prices from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List
import logging
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.db_manager import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataCollector:
    """Collects and stores stock price data with technical indicators."""
    
    def __init__(self):
        self.db = get_db_manager()
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for stock data."""
        # Simple Moving Averages
        df['sma_20'] = df['close_price'].rolling(window=20).mean()
        df['sma_50'] = df['close_price'].rolling(window=50).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close_price'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close_price'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bollinger_middle'] = df['close_price'].rolling(window=20).mean()
        std = df['close_price'].rolling(window=20).std()
        df['bollinger_upper'] = df['bollinger_middle'] + (std * 2)
        df['bollinger_lower'] = df['bollinger_middle'] - (std * 2)
        
        return df
    
    def fetch_stock_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Fetch historical stock data from Yahoo Finance."""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Reset index to make Date a column
            df = df.reset_index()
            
            # Rename columns - yfinance uses capitalized names
            column_mapping = {
                'Date': 'price_date',
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Keep only the columns we need
            df = df[['price_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
            
            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)
            
            # Convert date to proper format
            df['price_date'] = pd.to_datetime(df['price_date']).dt.date
            
            logger.info(f"Fetched {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()
    
    def store_stock_data(self, symbol: str, df: pd.DataFrame) -> int:
        """Store stock price data in database."""
        if df.empty:
            logger.warning(f"No data to store for {symbol}")
            return 0
        
        try:
            # Get stock_id
            stock_id = self.db.get_stock_id(symbol)
            if not stock_id:
                logger.error(f"Stock {symbol} not found in database")
                return 0
            
            # Prepare data
            df['stock_id'] = stock_id
            
            # Select columns
            columns = [
                'stock_id', 'price_date', 'open_price', 'high_price', 
                'low_price', 'close_price', 'volume', 'sma_20', 'sma_50',
                'ema_12', 'ema_26', 'rsi', 'macd', 'macd_signal',
                'bollinger_upper', 'bollinger_lower'
            ]
            
            # Replace NaN with None
            df = df[columns].replace({np.nan: None})
            
            # Create INSERT query
            query = """
                INSERT INTO stock_prices 
                (stock_id, price_date, open_price, high_price, low_price, 
                 close_price, volume, sma_20, sma_50, ema_12, ema_26, 
                 rsi, macd, macd_signal, bollinger_upper, bollinger_lower)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    open_price = VALUES(open_price),
                    high_price = VALUES(high_price),
                    low_price = VALUES(low_price),
                    close_price = VALUES(close_price),
                    volume = VALUES(volume),
                    sma_20 = VALUES(sma_20),
                    sma_50 = VALUES(sma_50),
                    ema_12 = VALUES(ema_12),
                    ema_26 = VALUES(ema_26),
                    rsi = VALUES(rsi),
                    macd = VALUES(macd),
                    macd_signal = VALUES(macd_signal),
                    bollinger_upper = VALUES(bollinger_upper),
                    bollinger_lower = VALUES(bollinger_lower)
            """
            
            # Convert to list of tuples
            data = [tuple(row) for row in df.values]
            
            # Execute
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, data)
                conn.commit()
                rows_affected = cursor.rowcount
                cursor.close()
            
            logger.info(f"Stored {rows_affected} price records for {symbol}")
            return rows_affected
            
        except Exception as e:
            logger.error(f"Error storing stock data: {e}")
            return 0
    
    def collect_and_store(self, symbols: List[str], start_date: str = None, end_date: str = None):
        """Collect and store data for multiple stocks."""
        results = {}
        
        for symbol in symbols:
            logger.info(f"Processing {symbol}...")
            
            # Fetch data
            df = self.fetch_stock_data(symbol, start_date, end_date)
            
            # Store data
            if not df.empty:
                rows = self.store_stock_data(symbol, df)
                results[symbol] = rows
            else:
                results[symbol] = 0
            
            # Rate limiting
            time.sleep(1)
        
        return results


def main():
    """Main execution function."""
    collector = StockDataCollector()
    
    # Stocks to track - all 6 companies
    symbols = ['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL', 'MSFT']
    
    logger.info("Starting stock data collection for 2 years...")
    logger.info(f"Collecting data for: {', '.join(symbols)}")
    results = collector.collect_and_store(symbols)
    
    logger.info("Collection complete:")
    for symbol, count in results.items():
        logger.info(f"  {symbol}: {count} records")


if __name__ == "__main__":
    main()
