#!/usr/bin/env python3
"""
Complete Setup Script for Stock ML Pipeline
This script will:
1. Initialize the database tables
2. Insert all 6 companies
3. Fetch 2 years of historical data
4. Verify the setup
"""

import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("=" * 70)
    print("STOCK ML PIPELINE - COMPLETE SETUP")
    print("=" * 70)
    print()
    print("This will set up your database with 2 years of stock data for:")
    print("  • AAPL (Apple Inc.)")
    print("  • TSLA (Tesla Inc.)")
    print("  • AMZN (Amazon.com Inc.)")
    print("  • NVDA (NVIDIA Corporation)")
    print("  • GOOGL (Alphabet Inc.)")
    print("  • MSFT (Microsoft Corporation)")
    print()
    
    # Check if database credentials are set
    if not os.getenv('MYSQLHOST'):
        print("⚠️  WARNING: Database credentials not found in environment")
        print("   Make sure to set these environment variables:")
        print("   - MYSQLHOST")
        print("   - MYSQLPORT")
        print("   - MYSQLDATABASE")
        print("   - MYSQLUSER")
        print("   - MYSQLPASSWORD")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    print("=" * 70)
    print("STEP 1: Initialize Database")
    print("=" * 70)
    
    try:
        from scripts.populate_stocks import main as populate_main
        populate_main()
    except Exception as e:
        print(f"❌ ERROR in populate_stocks: {e}")
        print("\nTrying alternative method...")
        
        # Alternative: use init_database script
        try:
            from scripts.init_database import main as init_main
            init_main()
        except Exception as e2:
            print(f"❌ ERROR in init_database: {e2}")
            print("\nPlease check your database connection and try again.")
            return
    
    print()
    print("=" * 70)
    print("STEP 2: Verify Setup")
    print("=" * 70)
    
    try:
        from src.database.db_manager import get_db_manager
        
        db = get_db_manager()
        
        # Check stocks
        stocks_query = "SELECT COUNT(*) as count FROM stocks"
        stocks_result = db.fetch_dict(stocks_query)
        stock_count = stocks_result[0]['count'] if stocks_result else 0
        
        # Check prices
        prices_query = "SELECT COUNT(*) as count FROM stock_prices"
        prices_result = db.fetch_dict(prices_query)
        price_count = prices_result[0]['count'] if prices_result else 0
        
        # Check by stock
        print("\nData per stock:")
        for symbol in ['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL', 'MSFT']:
            query = """
                SELECT COUNT(*) as count, MIN(sp.date) as earliest, MAX(sp.date) as latest
                FROM stocks s
                JOIN stock_prices sp ON s.stock_id = sp.stock_id
                WHERE s.symbol = %s
            """
            result = db.fetch_dict(query, (symbol,))
            if result and result[0]['count'] > 0:
                count = result[0]['count']
                earliest = result[0]['earliest']
                latest = result[0]['latest']
                print(f"  ✓ {symbol:6} - {count:4} records ({earliest} to {latest})")
            else:
                print(f"  ✗ {symbol:6} - No data found")
        
        print()
        print("=" * 70)
        print("SETUP COMPLETE!")
        print("=" * 70)
        print(f"✓ {stock_count} companies in database")
        print(f"✓ {price_count} total price records")
        print(f"✓ Average {price_count // stock_count if stock_count > 0 else 0} records per stock")
        print()
        print("Next steps:")
        print("  1. Start the backend: python src/api/main.py")
        print("  2. Start the frontend: cd frontend && npm run dev")
        print("  3. Open http://localhost:5173")
        print()
        
    except Exception as e:
        print(f"❌ ERROR during verification: {e}")
        print("\nSetup may be incomplete. Please check the errors above.")

if __name__ == "__main__":
    main()
