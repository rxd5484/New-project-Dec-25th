"""
FastAPI Backend for Stock ML Pipeline
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database.db_manager import get_db_manager

# Initialize FastAPI
app = FastAPI(
    title="Stock ML Pipeline API",
    description="API for stock predictions and sentiment analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
db = get_db_manager()


# Pydantic models
class StockInfo(BaseModel):
    symbol: str
    company_name: str
    sector: Optional[str]
    industry: Optional[str]


class PriceData(BaseModel):
    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Stock ML Pipeline API",
        "version": "1.0.0",
        "endpoints": [
            "/stocks",
            "/stocks/{symbol}",
            "/stocks/{symbol}/prices",
            "/health"
        ]
    }


@app.get("/stocks", response_model=List[StockInfo])
async def get_stocks():
    """Get all tracked stocks"""
    query = "SELECT symbol, company_name, sector, industry FROM stocks"
    stocks = db.fetch_dict(query)
    return stocks


@app.get("/stocks/{symbol}", response_model=StockInfo)
async def get_stock(symbol: str):
    """Get specific stock info"""
    query = """
        SELECT symbol, company_name, sector, industry 
        FROM stocks 
        WHERE symbol = %s
    """
    result = db.fetch_dict(query, (symbol.upper(),))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    
    return result[0]


@app.get("/stocks/{symbol}/prices", response_model=List[PriceData])
async def get_stock_prices(
    symbol: str,
    days: int = Query(30, ge=1, le=365)
):
    """Get historical prices"""
    query = """
        SELECT 
            sp.price_date as date,
            sp.open_price,
            sp.high_price,
            sp.low_price,
            sp.close_price,
            sp.volume
        FROM stocks s
        JOIN stock_prices sp ON s.stock_id = sp.stock_id
        WHERE s.symbol = %s
        ORDER BY sp.price_date DESC
        LIMIT %s
    """
    
    prices = db.fetch_dict(query, (symbol.upper(), days))
    
    if not prices:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    
    # Convert dates to strings
    for price in prices:
        price['date'] = price['date'].isoformat()
    
    return prices[::-1]  # Reverse for chronological order


@app.get("/health")
async def health_check():
    """Health check"""
    try:
        db.test_connection()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
MAINPY
