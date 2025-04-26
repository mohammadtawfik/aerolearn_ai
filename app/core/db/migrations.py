"""
Database migration and verification tools for AeroLearn AI.
Provides utilities for creating, dropping, and inspecting database tables.
"""

from .schema import Base, DB_URL
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

def create_all_tables():
    """Create all tables defined in the Base metadata."""
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    print("All tables created.")
    return list_tables()

def drop_all_tables():
    """Drop all tables defined in the Base metadata."""
    engine = create_engine(DB_URL)
    Base.metadata.drop_all(engine)
    print("All tables dropped.")

def list_tables():
    """List all tables in the database."""
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in database:", tables)
    return tables

def verify_schema():
    """Verify that the database schema matches the expected schema."""
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Get expected tables from metadata
    expected_tables = Base.metadata.tables.keys()
    
    # Check if all expected tables exist
    missing_tables = [table for table in expected_tables if table not in tables]
    if missing_tables:
        print(f"Missing tables: {missing_tables}")
        return False
    
    # Check if all columns exist with correct types
    for table_name in expected_tables:
        table = Base.metadata.tables[table_name]
        db_columns = {col['name']: col for col in inspector.get_columns(table_name)}
        
        for column in table.columns:
            if column.name not in db_columns:
                print(f"Missing column: {table_name}.{column.name}")
                return False
    
    print("Schema verification passed.")
    return True

def get_table_details(table_name):
    """Get detailed information about a specific table."""
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    
    if table_name not in inspector.get_table_names():
        print(f"Table '{table_name}' does not exist.")
        return None
    
    columns = inspector.get_columns(table_name)
    primary_keys = inspector.get_primary_keys(table_name)
    foreign_keys = inspector.get_foreign_keys(table_name)
    
    return {
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys
    }

def run_migration(version=None):
    """
    Run migration to specified version or latest.
    This is a placeholder for future implementation with a proper migration tool.
    """
    print(f"Running migration to version: {version or 'latest'}")
    create_all_tables()
    verify_schema()

# Usage for manual dev setup:
# from app.core.db.migrations import create_all_tables, verify_schema
# create_all_tables()
# verify_schema()
