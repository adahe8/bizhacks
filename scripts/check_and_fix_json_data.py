#!/usr/bin/env python3
# scripts/fix_csv_json_format.py

"""
Script to fix JSON format in users.csv file
Converts {item1,item2,item3} to ["item1","item2","item3"]
"""

import csv
import json
import sys
import os

def convert_curly_to_json_array(value):
    """Convert {item1,item2,item3} format to ["item1","item2","item3"]"""
    if not value or not isinstance(value, str):
        return value
    
    # Check if it's already valid JSON
    try:
        json.loads(value)
        return value
    except:
        pass
    
    # Check if it matches the curly brace pattern
    if value.startswith('{') and value.endswith('}'):
        # Remove the curly braces
        content = value[1:-1]
        
        # Handle empty set
        if not content:
            return '[]'
        
        # Split by comma, but be careful with commas inside values
        items = []
        current_item = ""
        in_quotes = False
        
        for char in content:
            if char == '"' and (not current_item or current_item[-1] != '\\'):
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                # End of item
                cleaned_item = current_item.strip().strip('"').strip("'")
                if cleaned_item:
                    items.append(cleaned_item)
                current_item = ""
            else:
                current_item += char
        
        # Don't forget the last item
        if current_item:
            cleaned_item = current_item.strip().strip('"').strip("'")
            if cleaned_item:
                items.append(cleaned_item)
        
        # Convert to JSON array
        return json.dumps(items)
    
    return value

def fix_csv_file(input_file='users.csv', output_file=None):
    """Fix JSON format in CSV file"""
    if output_file is None:
        output_file = input_file
    
    print(f"Reading from: {input_file}")
    print(f"Will write to: {output_file}")
    print()
    
    # Read all data
    rows = []
    headers = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        for row in reader:
            rows.append(row)
    
    print(f"Found {len(rows)} rows to process")
    
    # Process each row
    fixed_count = 0
    for i, row in enumerate(rows):
        row_fixed = False
        
        # Fix channels_engaged
        if 'channels_engaged' in row and row['channels_engaged']:
            original = row['channels_engaged']
            converted = convert_curly_to_json_array(original)
            
            if original != converted:
                row['channels_engaged'] = converted
                row_fixed = True
                if i < 5:  # Show first 5 fixes
                    print(f"Row {i+1} - Fixed channels_engaged:")
                    print(f"  From: {original}")
                    print(f"  To:   {converted}")
        
        # Fix purchase_history
        if 'purchase_history' in row and row['purchase_history']:
            original = row['purchase_history']
            converted = convert_curly_to_json_array(original)
            
            if original != converted:
                row['purchase_history'] = converted
                row_fixed = True
                if i < 5:  # Show first 5 fixes
                    print(f"Row {i+1} - Fixed purchase_history:")
                    print(f"  From: {original}")
                    print(f"  To:   {converted}")
        
        if row_fixed:
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} rows")
    
    # Write back to file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Successfully wrote fixed data to: {output_file}")
    
    # Verify the fix
    print("\n=== Verifying fixed data ===")
    invalid_count = 0
    
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            # Check channels_engaged
            if row.get('channels_engaged'):
                try:
                    json.loads(row['channels_engaged'])
                except json.JSONDecodeError as e:
                    print(f"Row {i+1} - Invalid channels_engaged: {e}")
                    print(f"  Value: {row['channels_engaged']}")
                    invalid_count += 1
            
            # Check purchase_history
            if row.get('purchase_history'):
                try:
                    json.loads(row['purchase_history'])
                except json.JSONDecodeError as e:
                    print(f"Row {i+1} - Invalid purchase_history: {e}")
                    print(f"  Value: {row['purchase_history']}")
                    invalid_count += 1
    
    if invalid_count == 0:
        print("✅ All JSON data is now valid!")
    else:
        print(f"❌ Still found {invalid_count} invalid JSON values")

def main():
    """Main function"""
    # Check if users.csv exists
    if not os.path.exists('users.csv'):
        print("Error: users.csv not found in current directory")
        sys.exit(1)
    
    # Create backup first
    import shutil
    backup_file = 'users.csv.backup'
    print(f"Creating backup: {backup_file}")
    shutil.copy2('users.csv', backup_file)
    
    # Fix the CSV file
    fix_csv_file('users.csv')
    
    print(f"\nBackup saved as: {backup_file}")
    print("If you need to restore, run: cp users.csv.backup users.csv")

if __name__ == "__main__":
    main()