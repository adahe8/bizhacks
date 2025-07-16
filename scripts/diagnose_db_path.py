#!/usr/bin/env python3
"""
Script to diagnose database path issues
"""

import os
import sys
import glob

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def find_campaign_db_files():
    """Find all campaign.db files in the project"""
    print("SEARCHING FOR campaign.db FILES")
    print("="*60)
    
    # Get project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(f"Project root: {project_root}\n")
    
    # Search for all campaign.db files
    print("Found campaign.db files:")
    found_files = []
    
    for root, dirs, files in os.walk(project_root):
        # Skip venv and node_modules
        dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '.git', '__pycache__']]
        
        for file in files:
            if file == 'campaign.db':
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_root)
                size = os.path.getsize(full_path) / 1024  # KB
                found_files.append((rel_path, full_path, size))
                print(f"  - {rel_path} ({size:.2f} KB)")
    
    if not found_files:
        print("  No campaign.db files found!")
    
    return found_files

def check_database_configs():
    """Check database configuration from different locations"""
    print("\n\nDATABASE CONFIGURATION")
    print("="*60)
    
    # Check environment variable
    db_url_env = os.environ.get('DATABASE_URL', 'Not set')
    print(f"DATABASE_URL from environment: {db_url_env}")
    
    # Check settings
    try:
        from backend.core.config import settings
        print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")
    except ImportError:
        try:
            from core.config import settings
            print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")
        except ImportError:
            print("Could not import settings")
    
    # Parse the URL to get the path
    if "sqlite:///" in str(db_url_env):
        db_path = str(db_url_env).replace("sqlite:///", "")
        if db_path.startswith("./"):
            print(f"\nRelative path detected: {db_path}")
            print("This will create different databases when run from different directories!")
            
            # Show what the absolute path would be from different locations
            cwd = os.getcwd()
            abs_from_cwd = os.path.abspath(os.path.join(cwd, db_path.replace("./", "")))
            print(f"\nFrom current directory ({cwd}):")
            print(f"  Would use: {abs_from_cwd}")
            
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            abs_from_root = os.path.abspath(os.path.join(project_root, db_path.replace("./", "")))
            print(f"\nFrom project root ({project_root}):")
            print(f"  Would use: {abs_from_root}")

def check_demo_files():
    """Check if demo CSV files exist"""
    print("\n\nDEMO DATA FILES")
    print("="*60)
    
    demo_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'demo')
    print(f"Demo directory: {demo_path}")
    print(f"Exists: {os.path.exists(demo_path)}")
    
    if os.path.exists(demo_path):
        print("\nDemo files:")
        for file in ['companies.csv', 'products.csv', 'users.csv', 'content_assets.csv', 'metrics.csv']:
            file_path = os.path.join(demo_path, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  ✓ {file} ({size} bytes)")
            else:
                print(f"  ✗ {file} (missing)")

def suggest_fix():
    """Suggest how to fix the issues"""
    print("\n\nRECOMMENDED FIX")
    print("="*60)
    print("1. Update your .env file to use an absolute path:")
    print("   DATABASE_URL=sqlite:///absolute/path/to/project/campaign.db")
    print("\n2. Or use a path relative to the project root:")
    print("   DATABASE_URL=sqlite:///../campaign.db")
    print("\n3. Then run the initialization script:")
    print("   cd scripts")
    print("   python init_database.py --force")
    print("\n4. Always run scripts from the same directory (preferably project root)")

def main():
    """Main diagnostic function"""
    print("DATABASE PATH DIAGNOSTIC")
    print("="*60)
    print(f"Current working directory: {os.getcwd()}\n")
    
    # Find all database files
    db_files = find_campaign_db_files()
    
    # Check configurations
    check_database_configs()
    
    # Check demo files
    check_demo_files()
    
    # Suggest fixes
    suggest_fix()

if __name__ == "__main__":
    main()