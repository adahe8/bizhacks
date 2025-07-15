#!/usr/bin/env python3
"""
Simple script to print all table schemas from the SQLModel database
No external dependencies required beyond project requirements
"""

import sys
import os
from sqlalchemy import inspect
from sqlmodel import Session

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force the database to be at project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(project_root, 'campaign.db')

# Check if database exists in backend directory (where it was created)
backend_db_path = os.path.join(project_root, 'backend', 'campaign.db')
if os.path.exists(backend_db_path) and not os.path.exists(db_path):
    print(f"Found database in backend directory: {backend_db_path}")
    db_path = backend_db_path

# Set the database URL before importing
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

# Now import after setting the environment variable
from data.database import engine
from data.models import (
    Company, Product, User, Campaign, ContentAsset,
    Metric, CustomerSegment, Schedule, SetupConfiguration,
    Transaction, GameState, CampaignMetrics
)

def print_separator(char='-', length=80):
    """Print a separator line"""
    print(char * length)

def print_header(text, char='='):
    """Print a formatted header"""
    print_separator(char)
    print(f"{text:^80}")
    print_separator(char)

def print_table_schema(inspector, table_name):
    """Print schema information for a single table"""
    print(f"\nTABLE: {table_name}")
    print_separator()
    
    # Get columns
    columns = inspector.get_columns(table_name)
    
    # Print column headers
    print(f"{'Column':<25} {'Type':<20} {'Nullable':<10} {'Key':<15}")
    print_separator('-', 70)
    
    # Print each column
    for col in columns:
        col_name = col['name']
        col_type = str(col['type'])
        nullable = 'YES' if col['nullable'] else 'NO'
        key = 'PRIMARY KEY' if col.get('primary_key') else ''
        
        print(f"{col_name:<25} {col_type:<20} {nullable:<10} {key:<15}")
    
    # Get and print foreign keys
    foreign_keys = inspector.get_foreign_keys(table_name)
    if foreign_keys:
        print("\nForeign Keys:")
        for fk in foreign_keys:
            const_cols = ', '.join(fk['constrained_columns'])
            ref_cols = ', '.join(fk['referred_columns'])
            print(f"  - {const_cols} -> {fk['referred_table']}.{ref_cols}")
    
    # Get and print indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print("\nIndexes:")
        for idx in indexes:
            cols = ', '.join(idx['column_names'])
            unique = 'UNIQUE' if idx['unique'] else 'NON-UNIQUE'
            print(f"  - {idx['name']}: {cols} ({unique})")

def get_table_counts(session):
    """Get row counts for all tables"""
    models = [
        (Company, "companies"),
        (Product, "products"),
        (User, "users"),
        (Campaign, "campaigns"),
        (ContentAsset, "content_assets"),
        (Metric, "metrics"),
        (CustomerSegment, "customer_segments"),
        (Schedule, "schedules"),
        (SetupConfiguration, "setup_configurations"),
        (Transaction, "transactions"),
        (GameState, "game_state"),
        (CampaignMetrics, "campaign_metrics")
    ]
    
    print_header("TABLE ROW COUNTS")
    
    # Check if any tables exist first
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if not inspector.get_table_names():
        print("No tables exist in the database yet.")
        return
    
    print(f"{'Table':<30} {'Row Count':<15}")
    print_separator('-', 45)
    
    total_rows = 0
    
    for model, table_name in models:
        try:
            count = session.query(model).count()
            print(f"{table_name:<30} {count:<15}")
            total_rows += count
        except Exception as e:
            print(f"{table_name:<30} {'Error':<15}")
    
    print_separator('-', 45)
    print(f"{'TOTAL':<30} {total_rows:<15}")

def main():
    """Main function to print all database schema information"""
    print_header("BIZHACKS DATABASE SCHEMA INSPECTION", '=')
    print(f"Database URL: {engine.url}\n")
    
    # Create inspector
    inspector = inspect(engine)
    
    # Get all table names
    table_names = inspector.get_table_names()
    
    if not table_names:
        print("ERROR: No tables found in the database!")
        print(f"Database location: {engine.url}")
        print("\nPlease run the initialization script first:")
        print("  cd scripts")
        print("  python init_database.py")
        return
    
    print(f"Found {len(table_names)} tables in the database\n")
    
    # Print schema for each table
    for table_name in sorted(table_names):
        print_table_schema(inspector, table_name)
        print()  # Add spacing between tables
    
    # Get row counts
    with Session(engine) as session:
        get_table_counts(session)
    
    # Print summary
    print_header("SUMMARY")
    print(f"Total tables: {len(table_names)}")
    print(f"Tables: {', '.join(sorted(table_names))}")
    print()

if __name__ == "__main__":
    main()