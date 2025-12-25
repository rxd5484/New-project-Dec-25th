# New-project-Dec-25th
📈 Stock Market ML Pipeline with Real-Time Sentiment Analysis
A production-ready machine learning pipeline that combines financial sentiment analysis with stock price prediction, featuring real-time data processing, MySQL database integration, and an interactive dashboard.
🎯 Project Overview
This project demonstrates end-to-end ML engineering capabilities by:

Collecting real-time financial news and stock market data
Performing sentiment analysis using transformer models
Predicting stock prices with LSTM networks
Storing and querying data efficiently in MySQL
Serving predictions through a REST API
Visualizing results in an interactive dashboard

🏗️ Architecture
Data Sources (News API, Yahoo Finance)
            ↓
    Data Collection Layer
            ↓
      ETL Pipeline
            ↓
    MySQL Database (Optimized Schema)
            ↓
    ML Processing Layer
    ├── Sentiment Analysis (DistilBERT)
    └── Price Prediction (LSTM)
            ↓
    FastAPI Backend
            ↓
    React Dashboard
🛠️ Technical Stack

Database: MySQL 8.0+ with optimized indexing
Backend: Python 3.9+, FastAPI
ML/AI: PyTorch, Transformers, scikit-learn
Data Processing: pandas, numpy
API Integration: yfinance, newsapi-python
Frontend: React, Chart.js
Deployment: Docker, docker-compose

📊 Database Schema
The project uses a normalized MySQL schema with proper indexing:

stocks - Stock information and metadata
stock_prices - Historical OHLCV data (indexed)
news_articles - Financial news with sentiment scores
predictions - ML model predictions with confidence scores
model_metrics - Training metrics and performance tracking

🚀 Quick Start
Prerequisites
bash- Python 3.9+
- MySQL 8.0+
- Node.js 16+ (for dashboard)
- Docker (optional)
Installation

Clone the repository

bashgit clone <your-repo-url>
cd stock-ml-pipeline

Set up Python environment

bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Configure MySQL

bash# Create database
mysql -u root -p
CREATE DATABASE stock_ml_db;
exit;

# Update config.yaml with your credentials

Initialize database schema

bashpython scripts/init_database.py

Run the data pipeline

bashpython src/data_collection/collect_data.py

Train ML models

bashpython src/models/train_sentiment.py
python src/models/train_predictor.py

Start the API server

bashuvicorn src.api.main:app --reload

Launch the dashboard

🔑 Key Features
1. Data Collection

Real-time stock price data from Yahoo Finance
Financial news from News API
Automated ETL pipeline with error handling
Data validation and cleaning

2. Machine Learning Models
Sentiment Analysis

Model: DistilBERT fine-tuned on financial text
Input: News headlines and articles
Output: Sentiment score (-1 to 1)
Accuracy: ~85% on financial sentiment datasets

Price Prediction

Model: LSTM with attention mechanism
Features: OHLCV data + sentiment scores + technical indicators
Output: Next-day price prediction
Evaluation: RMSE, MAE, directional accuracy

3. Database Optimization

Composite indexes on (symbol, timestamp)
Partitioning for historical data
Query optimization for time-series operations
Connection pooling for concurrent access

4. REST API

/api/stocks/{symbol} - Get stock information
/api/predict/{symbol} - Get price predictions
/api/sentiment/{symbol} - Get sentiment analysis
/api/metrics - Model performance metrics

5. Dashboard

Real-time price charts
Sentiment timeline visualization
Prediction confidence intervals
Model performance metrics


🧪 Testing
bash# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Check code coverage
pytest --cov=src tests/

🤝 Contributing
This is a portfolio project, but suggestions are welcome! Please open an issue or submit a pull request.
📄 License
MIT License - feel free to use this project for learning and portfolio purposes.
👤 Author
Name: Rakshit Dongre

LinkedIn: 
GitHub: rxd5484
Email: dongre28030@gmail.com//dongre2003@gmail.com


Note: This project is for educational and portfolio purposes only. Not financial advice.

Some Screenshots:
<img width="1176" height="391" alt="Screenshot 2025-12-25 at 9 43 17 PM" src="https://github.com/user-attachments/assets/a0131f84-c737-4e92-ab6d-c838080a7e97" />

<img width="1139" height="381" alt="Screenshot 2025-12-25 at 9 43 24 PM" src="https://github.com/user-attachments/assets/5c3d5a9a-b516-4637-a101-8e670f4ab10e" />
<img width="1339" height="545" alt="Screenshot 2025-12-25 at 9 43 59 PM" src="https://github.com/user-attachments/assets/832f96cb-aedd-496b-b873-92480cf5b340" />
<img width="1390" height="563" alt="Screenshot 2025-12-25 at 9 44 46 PM" src="https://github.com/user-attachments/assets/a1786b9d-690c-496e-8629-fa6bde9ad9e0" />





<img width="1395" height="542" alt="Screenshot 2025-12-25 at 9 45 12 PM" src="https://github.com/user-attachments/assets/83cd3cb2-b6ff-40e9-8fd5-44f445fb8f26" />
<img width="1395" height="720" alt="Screenshot 2025-12-25 at 9 45 19 PM" src="https://github.com/user-attachments/assets/113b922c-cd46-458e-8d0d-0b00e8adf6d6" />






