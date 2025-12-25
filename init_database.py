#!/usr/bin/env python3
"""
Database Initialization Script
Sets up the MySQL database and creates initial schema
"""

import mysql.connector
from mysql.connector import Error
import yaml
from pathlib import Path
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    """Load database configuration."""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('database', {})
    else:
        return {
            'host': 'localhost',
            'port': 3306,
            'database': 'stock_ml_db',
            'user': 'root',
            'password': ''
        }


def create_connection(config, database=None):
    """Create MySQL connection."""
    try:
        connection = mysql.connector.connect(
            host=config['host'],
            port=config.get('port', 3306),
            user=config['user'],
            password=config['password'],
            database=database
        )
        logger.info(f"Connected to MySQL server")
        return connection
    except Error as e:
        logger.error(f"Connection error: {e}")
        return None


def create_database(config):
    """Create the database if it doesn't exist."""
    connection = create_connection(config)
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Create database
        database_name = config['database']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        logger.info(f"Database '{database_name}' created successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        logger.error(f"Error creating database: {e}")
        return False


def execute_schema(config):
    """Execute the schema SQL file."""
    schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
    
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        return False
    
    # Read schema file
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Connect with database selected
    connection = create_connection(config, database=config['database'])
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Split by semicolons and execute each statement
        statements = schema_sql.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except Error as e:
                    # Some statements may fail if objects already exist
                    if "already exists" not in str(e):
                        logger.warning(f"Statement execution warning: {e}")
        
        connection.commit()
        logger.info("Schema executed successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        logger.error(f"Error executing schema: {e}")
        return False


def verify_setup(config):
    """Verify the database setup."""
    connection = create_connection(config, database=config['database'])
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        expected_tables = [
            'stocks', 'stock_prices', 'news_articles', 
            'predictions', 'model_metrics', 'feature_importance',
            'data_quality_logs'
        ]
        
        found_tables = [table[0] for table in tables]
        
        logger.info(f"Found {len(found_tables)} tables:")
        for table in found_tables:
            logger.info(f"  - {table}")
        
        # Check if sample stocks exist
        cursor.execute("SELECT COUNT(*) FROM stocks")
        stock_count = cursor.fetchone()[0]
        logger.info(f"Found {stock_count} stocks in database")
        
        cursor.close()
        connection.close()
        
        return len(found_tables) >= len(expected_tables)
        
    except Error as e:
        logger.error(f"Verification error: {e}")
        return False


def main():
    """Main initialization function."""
    logger.info("=== Stock ML Database Initialization ===")
    
    # Load configuration
    config = load_config()
    logger.info(f"Loaded configuration for database: {config['database']}")
    
    # Step 1: Create database
    logger.info("\n1. Creating database...")
    if not create_database(config):
        logger.error("Failed to create database")
        sys.exit(1)
    
    # Step 2: Execute schema
    logger.info("\n2. Executing schema...")
    if not execute_schema(config):
        logger.error("Failed to execute schema")
        sys.exit(1)
    
    # Step 3: Verify setup
    logger.info("\n3. Verifying setup...")
    if verify_setup(config):
        logger.info("\n✓ Database initialization complete!")
        logger.info("\nNext steps:")
        logger.info("1. Update config.yaml with your database password")
        logger.info("2. Run: python src/data_collection/collect_data.py")
        logger.info("3. Run: python src/models/train_sentiment.py")
        logger.info("4. Run: python src/models/train_predictor.py")
        logger.info("5. Start API: uvicorn src.api.main:app --reload")
    else:
        logger.error("\n✗ Database verification failed")
        sys.exit(1)


if __name__ == "__main__":
    main()