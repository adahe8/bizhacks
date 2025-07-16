# BizHacks Scripts

This directory contains utility scripts for the BizHacks project.

## Available Scripts

### print_db_schemas.py
Prints all table schemas from the SQLModel database with detailed formatting.

**Features:**
- Lists all tables in the database
- Shows column details (name, type, nullable, primary keys)
- Displays foreign key relationships
- Shows indexes
- Provides row counts for each table
- Requires `tabulate` package for pretty formatting

**Usage:**
```bash
cd scripts
python print_db_schemas.py
```

### print_db_schemas_simple.py
A simpler version of the schema printer that doesn't require external dependencies.

**Features:**
- Same functionality as above but with basic formatting
- No additional dependencies beyond project requirements
- Lighter weight alternative

**Usage:**
```bash
cd scripts
python print_db_schemas_simple.py
```

## Setup

Make sure you're in the project root directory and have activated your virtual environment:

```bash
# From project root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements if not already done
pip install -r requirements.txt

# For the enhanced version, also install:
pip install tabulate
```

## Example Output

```
BIZHACKS DATABASE SCHEMA INSPECTION
================================================================================
Database URL: sqlite:///campaign.db

Found 12 tables in the database

TABLE: campaigns
--------------------------------------------------------------------------------
Column                    Type                 Nullable   Key            
------------------------------------------------------------------------
id                        CHAR(32)             NO         PRIMARY KEY    
product_id                CHAR(32)             YES                       
name                      VARCHAR              NO                        
description               VARCHAR              YES                       
...

Foreign Keys:
  - product_id -> products.id

TABLE ROW COUNTS
================================================================================
Table                          Row Count      
----------------------------------------------
companies                      2              
products                       2              
users                          3              
...
```

## Creating New Scripts

When adding new scripts to this directory:

1. Add the parent directory to Python path:
   ```python
   import sys
   import os
   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
   ```

2. Import project modules as needed:
   ```python
   from data.database import engine
   from data.models import Company, Product, User
   ```

3. Make scripts executable:
   ```bash
   chmod +x script_name.py
   ```

4. Add a shebang line:
   ```python
   #!/usr/bin/env python3
   ```