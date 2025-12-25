CREATE DATABASE IF NOT EXISTS stock_ml_db;
USE stock_ml_db;

CREATE TABLE IF NOT EXISTS stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_sector (sector)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS stock_prices (
    price_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(12, 4) NOT NULL,
    high_price DECIMAL(12, 4) NOT NULL,
    low_price DECIMAL(12, 4) NOT NULL,
    close_price DECIMAL(12, 4) NOT NULL,
    adj_close DECIMAL(12, 4),
    volume BIGINT NOT NULL,
    -- Technical indicators
    sma_20 DECIMAL(12, 4),
    sma_50 DECIMAL(12, 4),
    ema_12 DECIMAL(12, 4),
    ema_26 DECIMAL(12, 4),
    rsi DECIMAL(5, 2),
    macd DECIMAL(12, 4),
    macd_signal DECIMAL(12, 4),
    bollinger_upper DECIMAL(12, 4),
    bollinger_lower DECIMAL(12, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    -- Composite index for time-series queries
    INDEX idx_stock_date (stock_id, price_date DESC),
    INDEX idx_date (price_date),
    UNIQUE KEY unique_stock_date (stock_id, price_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS news_articles (
    article_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    source VARCHAR(255),
    author VARCHAR(255),
    url TEXT,
    published_at DATETIME NOT NULL,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Sentiment analysis results
    sentiment_score DECIMAL(5, 4), -- Range: -1.0 to 1.0
    sentiment_label VARCHAR(20), -- positive, negative, neutral
    confidence DECIMAL(5, 4), -- Model confidence 0.0 to 1.0
    model_version VARCHAR(50),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_stock_published (stock_id, published_at DESC),
    INDEX idx_published (published_at),
    INDEX idx_sentiment (sentiment_score),
    FULLTEXT INDEX idx_content (title, description, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS predictions (
    prediction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    prediction_date DATE NOT NULL,
    target_date DATE NOT NULL, -- Date being predicted
    predicted_price DECIMAL(12, 4) NOT NULL,
    actual_price DECIMAL(12, 4), -- Filled in after target_date
    prediction_type VARCHAR(50) NOT NULL, -- 'next_day', 'next_week', etc.
    confidence_lower DECIMAL(12, 4), -- Lower bound of confidence interval
    confidence_upper DECIMAL(12, 4), -- Upper bound of confidence interval
    -- Model metadata
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    -- Features used
    used_sentiment BOOLEAN DEFAULT FALSE,
    used_technical_indicators BOOLEAN DEFAULT TRUE,
    -- Evaluation metrics (calculated after actual_price is known)
    absolute_error DECIMAL(12, 4),
    percentage_error DECIMAL(8, 4),
    direction_correct BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_stock_target (stock_id, target_date DESC),
    INDEX idx_prediction_date (prediction_date),
    INDEX idx_model (model_name, model_version),
    UNIQUE KEY unique_stock_target_model (stock_id, target_date, model_name, prediction_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS model_metrics (
    metric_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'training', 'validation', 'test', 'production'
    evaluation_date DATE NOT NULL,
    -- Regression metrics
    rmse DECIMAL(12, 6),
    mae DECIMAL(12, 6),
    mape DECIMAL(8, 4),
    r_squared DECIMAL(8, 6),
    -- Classification metrics (for sentiment model)
    accuracy DECIMAL(8, 6),
    precision_score DECIMAL(8, 6),
    recall DECIMAL(8, 6),
    f1_score DECIMAL(8, 6),
    -- Directional accuracy (for price prediction)
    directional_accuracy DECIMAL(8, 6),
    -- Sample size
    sample_size INT,
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_version (model_name, model_version),
    INDEX idx_eval_date (evaluation_date DESC),
    INDEX idx_metric_type (metric_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS feature_importance (
    importance_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    importance_score DECIMAL(12, 8) NOT NULL,
    rank_position INT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_version (model_name, model_version),
    INDEX idx_importance_score (importance_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS data_quality_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    check_type VARCHAR(100) NOT NULL, -- 'missing_data', 'outlier', 'duplicate', etc.
    stock_id INT,
    affected_date DATE,
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    description TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE SET NULL,
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved),
    INDEX idx_check_type (check_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE OR REPLACE VIEW latest_stock_prices AS
SELECT 
    s.symbol,
    s.company_name,
    sp.price_date,
    sp.close_price,
    sp.volume,
    sp.rsi,
    ROUND(((sp.close_price - lag_close.close_price) / lag_close.close_price * 100), 2) as daily_change_pct
FROM stocks s
JOIN stock_prices sp ON s.stock_id = sp.stock_id
LEFT JOIN (
    SELECT stock_id, close_price, price_date,
           ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY price_date DESC) as rn
    FROM stock_prices
) lag_close ON s.stock_id = lag_close.stock_id AND lag_close.rn = 2
WHERE sp.price_date = (
    SELECT MAX(price_date) 
    FROM stock_prices 
    WHERE stock_id = s.stock_id
);

-- View: recent_sentiment
-- Average sentiment scores for past week by stock
CREATE OR REPLACE VIEW recent_sentiment AS
SELECT 
    s.symbol,
    s.company_name,
    COUNT(*) as article_count,
    ROUND(AVG(n.sentiment_score), 4) as avg_sentiment,
    ROUND(STDDEV(n.sentiment_score), 4) as sentiment_volatility,
    MAX(n.published_at) as latest_article
FROM stocks s
JOIN news_articles n ON s.stock_id = n.stock_id
WHERE n.published_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY s.stock_id, s.symbol, s.company_name;

-- View: model_performance_summary
-- Latest performance metrics for each model
CREATE OR REPLACE VIEW model_performance_summary AS
SELECT 
    mm.model_name,
    mm.model_version,
    mm.metric_type,
    mm.rmse,
    mm.mae,
    mm.r_squared,
    mm.directional_accuracy,
    mm.accuracy,
    mm.evaluation_date,
    mm.sample_size
FROM model_metrics mm
WHERE (mm.model_name, mm.model_version, mm.evaluation_date) IN (
    SELECT model_name, model_version, MAX(evaluation_date)
    FROM model_metrics
    GROUP BY model_name, model_version
)
ORDER BY mm.model_name, mm.model_version;

-- Stored Procedure: Calculate prediction accuracy
DELIMITER //
CREATE PROCEDURE calculate_prediction_accuracy(
    IN p_stock_id INT,
    IN p_date_from DATE,
    IN p_date_to DATE
)
BEGIN
    SELECT 
        model_name,
        model_version,
        COUNT(*) as total_predictions,
        ROUND(AVG(ABS(percentage_error)), 2) as avg_error_pct,
        ROUND(AVG(CASE WHEN direction_correct THEN 1 ELSE 0 END) * 100, 2) as directional_accuracy_pct,
        MIN(absolute_error) as best_prediction,
        MAX(absolute_error) as worst_prediction
    FROM predictions
    WHERE stock_id = p_stock_id
        AND target_date BETWEEN p_date_from AND p_date_to
        AND actual_price IS NOT NULL
    GROUP BY model_name, model_version
    ORDER BY avg_error_pct;
END //
DELIMITER ;

-- Insert sample stocks for testing
INSERT INTO stocks (symbol, company_name, sector, industry) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics'),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Content & Information'),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software'),
('TSLA', 'Tesla, Inc.', 'Consumer Cyclical', 'Auto Manufacturers'),
('NVDA', 'NVIDIA Corporation', 'Technology', 'Semiconductors')
ON DUPLICATE KEY UPDATE company_name = VALUES(company_name);


