"""
MySQL Database Connection Manager
Handles connection pooling, query execution, and transaction management
"""

import mysql.connector
from mysql.connector import pooling, Error
from typing import List, Dict, Any, Optional, Tuple
import logging
from contextlib import contextmanager
import yaml
from pathlib import Path
import os
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages MySQL database connections with connection pooling
    for efficient resource usage in production environments.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize database manager with configuration.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config = self._load_config(config_path)
        self.connection_pool = None
        self._initialize_pool()
    
    def _parse_database_url(self, url: str) -> Dict[str, Any]:
        """
        Parse DATABASE_URL environment variable.
        Format: mysql://user:password@host:port/database?params
        
        Args:
            url: Database URL string
            
        Returns:
            Dictionary with connection parameters
        """
        try:
            parsed = urlparse(url)
            
            config = {
                'host': parsed.hostname,
                'port': parsed.port or 3306,
                'database': parsed.path.lstrip('/').split('?')[0],
                'user': parsed.username,
                'password': parsed.password,
                'pool_name': 'stock_ml_pool',
                'pool_size': 5
            }
            
            # Handle SSL and other query parameters
            if 'sslaccept' in url or 'ssl' in url:
                config['ssl_disabled'] = False
            
            logger.info(f"Parsed DATABASE_URL for host: {config['host']}")
            return config
            
        except Exception as e:
            logger.error(f"Error parsing DATABASE_URL: {e}")
            raise
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load database configuration.
        Priority: DATABASE_URL > Railway env vars > config.yaml > defaults
        """
        # First, check for DATABASE_URL environment variable
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            logger.info("Using DATABASE_URL from environment")
            return self._parse_database_url(database_url)
        
        # Second, check for Railway-style individual env vars
        mysql_host = os.getenv('MYSQLHOST')
        if mysql_host:
            logger.info("Using Railway environment variables")
            return {
                'host': mysql_host,
                'port': int(os.getenv('MYSQLPORT', 3306)),
                'database': os.getenv('MYSQL_DATABASE') or os.getenv('MYSQLDATABASE', 'railway'),
                'user': os.getenv('MYSQLUSER', 'root'),
                'password': os.getenv('MYSQLPASSWORD', ''),
                'pool_name': 'stock_ml_pool',
                'pool_size': 5
            }
        
        # Third, try loading from config file
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    logger.info(f"Loaded config from {config_path}")
                    return config.get('database', {})
        except Exception as e:
            logger.warning(f"Error loading config file: {e}")
        
        # Finally, use defaults for local development
        logger.warning("Config file config.yaml not found. Using defaults.")
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default database configuration for local development."""
        return {
            'host': 'localhost',
            'port': 3306,
            'database': 'stock_ml_db',
            'user': 'root',
            'password': 'Ihb99ihb$@$@',
            'pool_name': 'stock_ml_pool',
            'pool_size': 5
        }
    
    def _initialize_pool(self):
        """Initialize connection pool for efficient connection management."""
        try:
            pool_config = {
                'pool_name': self.config.get('pool_name', 'stock_ml_pool'),
                'pool_size': self.config.get('pool_size', 5),
                'pool_reset_session': True,
                'host': self.config['host'],
                'port': self.config.get('port', 3306),
                'database': self.config['database'],
                'user': self.config['user'],
                'password': self.config['password']
            }
            
            # Add SSL config if present
            if self.config.get('ssl_disabled') is False:
                pool_config['ssl_disabled'] = False
            
            self.connection_pool = pooling.MySQLConnectionPool(**pool_config)
            logger.info(f"Database connection pool initialized successfully (host: {self.config['host']})")
        except Error as e:
            logger.error(f"Error initializing connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting database connection from pool.
        Ensures proper connection cleanup.
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
        """
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Tuple] = None,
        fetch: bool = True
    ) -> Optional[List[Tuple]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters for prepared statements
            fetch: Whether to fetch results
            
        Returns:
            List of tuples containing query results
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if fetch:
                    results = cursor.fetchall()
                    cursor.close()
                    return results
                else:
                    cursor.close()
                    return None
                    
        except Error as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def execute_many(
        self, 
        query: str, 
        data: List[Tuple]
    ) -> int:
        """
        Execute query with multiple parameter sets (bulk insert/update).
        
        Args:
            query: SQL query string
            data: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, data)
                conn.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                logger.info(f"Bulk operation affected {affected_rows} rows")
                return affected_rows
                
        except Error as e:
            logger.error(f"Bulk execution error: {e}")
            raise
    
    def execute_transaction(
        self, 
        queries: List[Tuple[str, Optional[Tuple]]]
    ) -> bool:
        """
        Execute multiple queries in a transaction.
        All queries succeed or all rollback.
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            True if transaction successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                try:
                    for query, params in queries:
                        cursor.execute(query, params or ())
                    
                    conn.commit()
                    cursor.close()
                    logger.info(f"Transaction completed: {len(queries)} queries")
                    return True
                    
                except Error as e:
                    conn.rollback()
                    cursor.close()
                    logger.error(f"Transaction rolled back: {e}")
                    return False
                    
        except Error as e:
            logger.error(f"Transaction error: {e}")
            return False
    
    def insert_one(
        self, 
        table: str, 
        data: Dict[str, Any]
    ) -> Optional[int]:
        """
        Insert a single row and return the auto-incremented ID.
        
        Args:
            table: Table name
            data: Dictionary of column names and values
            
        Returns:
            ID of inserted row or None if failed
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(data.values()))
                conn.commit()
                last_id = cursor.lastrowid
                cursor.close()
                logger.info(f"Inserted row into {table}, ID: {last_id}")
                return last_id
                
        except Error as e:
            logger.error(f"Insert error: {e}")
            return None
    
    def fetch_dict(
        self, 
        query: str, 
        params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute query and return results as list of dictionaries.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries with column names as keys
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                cursor.close()
                return results
                
        except Error as e:
            logger.error(f"Fetch dict error: {e}")
            return []
    
    def get_stock_id(self, symbol: str) -> Optional[int]:
        """
        Get stock_id for a given symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Stock ID or None if not found
        """
        query = "SELECT stock_id FROM stocks WHERE symbol = %s"
        result = self.execute_query(query, (symbol,))
        return result[0][0] if result else None
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                logger.info("Database connection test successful")
                return True
        except Error as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Singleton instance
_db_manager = None

def get_db_manager(config_path: str = "config.yaml") -> DatabaseManager:
    """
    Get singleton DatabaseManager instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(config_path)
    return _db_manager


if __name__ == "__main__":
    # Test database connection
    db = get_db_manager()
    
    if db.test_connection():
        print("✓ Database connection successful")
        
        # Test fetching stocks
        stocks = db.fetch_dict("SELECT * FROM stocks LIMIT 5")
        print(f"✓ Found {len(stocks)} stocks in database")
        
        for stock in stocks:
            print(f"  - {stock['symbol']}: {stock['company_name']}")
    else:
        print("✗ Database connection failed")    
    
 
