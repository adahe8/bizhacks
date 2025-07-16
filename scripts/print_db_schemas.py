#!/usr/bin/env python3
"""
Script to print all table schemas from the SQLModel database
"""

import sys
import os
from sqlalchemy import inspect, MetaData
from sqlmodel import Session, select
from tabulate import tabulate

# Add parent directory to path to import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import engine
from data.models import (
    Company, Product, User, Campaign, ContentAsset,
    Metric, CustomerSegment, Schedule, SetupConfiguration,
    Transaction, GameState, CampaignMetrics
)

def print_table_schema(inspector, table_name):
    """Print schema information for a single table"""
    print(f"\n{'='*60}")
    print(f"TABLE: {table_name}")
    print('='*60)
    
    # Get columns
    columns = inspector.get_columns(table_name)
    column_data = []
    
    for col in columns:
        column_data.append([
            col['name'],
            str(col['type']),
            'YES' if col['nullable'] else 'NO',
            col.get('default', ''),
            'PRIMARY KEY' if col.get('primary_key') else ''
        ])
    
    print(tabulate(
        column_data,
        headers=['Column', 'Type', 'Nullable', 'Default', 'Key'],
        tablefmt='grid'
    ))
    
    # Get foreign keys
    foreign_keys = inspector.get_foreign_keys(table_name)
    if foreign_keys:
        print("\nForeign Keys:")
        for fk in foreign_keys:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # Get indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print("\nIndexes:")
        for idx in indexes:
            print(f"  - {idx['name']}: {idx['column_names']} (unique: {idx['unique']})")

def get_model_info():
    """Get model class information"""
    models = [
        Company, Product, User, Campaign, ContentAsset,
        Metric, CustomerSegment, Schedule, SetupConfiguration,
        Transaction, GameState, CampaignMetrics
    ]
    
    print("\n" + "="*60)
    print("SQLMODEL MODELS")
    print("="*60)
    
    for model in models:
        print(f"\n{model.__name__} ({model.__tablename__}):")
        print(f"  Description: {model.__doc__ or 'No description'}")
        
        # Get relationships
        relationships = []
        for attr_name in dir(model):
            attr = getattr(model, attr_name)
            if hasattr(attr, 'property') and hasattr(attr.property, 'mapper'):
                relationships.append(attr_name)
        
        if relationships:
            print(f"  Relationships: {', '.join(relationships)}")

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
    
    print("\n" + "="*60)
    print("TABLE ROW COUNTS")
    print("="*60)
    
    count_data = []
    total_rows = 0
    
    for model, table_name in models:
        try:
            count = session.query(model).count()
            count_data.append([table_name, count])
            total_rows += count
        except Exception as e:
            count_data.append([table_name, f"Error: {str(e)}"])
    
    print(tabulate(count_data, headers=['Table', 'Row Count'], tablefmt='grid'))
    print(f"\nTotal rows across all tables: {total_rows}")

def main():
    """Main function to print all database schema information"""
    print("BIZHACKS DATABASE SCHEMA INSPECTION")
    print("="*60)
    print(f"Database URL: {engine.url}")
    
    # Create inspector
    inspector = inspect(engine)
    
    # Get all table names
    table_names = inspector.get_table_names()
    print(f"\nFound {len(table_names)} tables in the database")
    
    # Print model information
    get_model_info()
    
    # Print schema for each table
    for table_name in sorted(table_names):
        print_table_schema(inspector, table_name)
    
    # Get row counts
    with Session(engine) as session:
        get_table_counts(session)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total tables: {len(table_names)}")
    print(f"Tables: {', '.join(sorted(table_names))}")

if __name__ == "__main__":
    main()