"""
Fetch stock data from yfinance and populate the database.
Run this script to initialize your database with 2 years of stock data.
"""

import yfinance as yf
import mysql.connector
from datetime import datetime, timedelta
import os

# Top companies to track
COMPANIES = {
    'AAPL': 'Apple Inc.',
    'TSLA': 'Tesla Inc.',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corporation',
    'GOOGL': 'Alphabet Inc.',
    'MSFT': 'Microsoft Corporation'
}

def get_db_connection():
    """Get database connection using environment variables."""
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST', 'localhost'),
        port=int(os.getenv('MYSQLPORT', 3306)),
        database=os.getenv('MYSQL_DATABASE') or os.getenv('MYSQLDATABASE', 'railway'),
        user=os.getenv('MYSQLUSER', 'root'),
        password=os.getenv('MYSQLPASSWORD', '')
    )

def create_tables(cursor):
    """Create tables if they don't exist."""
    
    # Stocks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            stock_id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL UNIQUE,
            company_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Stock prices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            price_id INT AUTO_INCREMENT PRIMARY KEY,
            stock_id INT NOT NULL,
            date DATE NOT NULL,
            open DECIMAL(12, 4),
            high DECIMAL(12, 4),
            low DECIMAL(12, 4),
            close DECIMAL(12, 4),
            adj_close DECIMAL(12, 4),
            volume BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stock_id) REFERENCES stocks(stock_id),
            UNIQUE KEY unique_stock_date (stock_id, date)
        )
    """)
    
    print("✓ Tables created")

def insert_companies(cursor):
    """Insert company records."""
    for symbol, name in COMPANIES.items():
        cursor.execute("""
            INSERT IGNORE INTO stocks (symbol, company_name) 
            VALUES (%s, %s)
        """, (symbol, name))
    print(f"✓ Inserted {len(COMPANIES)} companies")

def fetch_and_insert_prices(cursor, conn):
    """Fetch 2 years of price data from yfinance and insert into database."""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # ~2 years
    
    for symbol in COMPANIES.keys():
        print(f"Fetching {symbol}...", end=" ")
        
        # Get stock_id
        cursor.execute("SELECT stock_id FROM stocks WHERE symbol = %s", (symbol,))
        result = cursor.fetchone()
        if not result:
            print(f"ERROR: {symbol} not found in stocks table")
            continue
        stock_id = result[0]
        
        # Fetch data from yfinance
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"WARNING: No data returned for {symbol}")
            continue
        
        # Insert price data
        rows_inserted = 0
        for date, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT IGNORE INTO stock_prices 
                    (stock_id, date, open, high, low, close, adj_close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    stock_id,
                    date.date(),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    float(row['Close']),  # yfinance history() returns adjusted prices in 'Close'
                    int(row['Volume'])
                ))
                rows_inserted += 1
            except Exception as e:
                print(f"Error inserting {symbol} {date}: {e}")
        
        conn.commit()
        print(f"✓ {rows_inserted} rows")

def main():
    print("=" * 50)
    print("Stock Database Initialization")
    print("=" * 50)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(f"✓ Connected to database")
        
        create_tables(cursor)
        conn.commit()
        
        insert_companies(cursor)
        conn.commit()
        
        fetch_and_insert_prices(cursor, conn)
        
        # Summary
        cursor.execute("SELECT COUNT(*) FROM stocks")
        stock_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM stock_prices")
        price_count = cursor.fetchone()[0]
        
        print("=" * 50)
        print(f"✓ Done! {stock_count} stocks, {price_count} price records")
        print("=" * 50)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
