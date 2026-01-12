-- Stock Market Database Schema

-- Stocks table (company info)
CREATE TABLE IF NOT EXISTS stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily price data
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
);

-- Index for faster queries
CREATE INDEX idx_stock_prices_date ON stock_prices(date);
CREATE INDEX idx_stock_prices_stock_date ON stock_prices(stock_id, date);
