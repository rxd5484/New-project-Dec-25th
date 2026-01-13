#!/usr/bin/env python3
"""Fix ALL Decimal conversion issues"""

import re

# Read the file
with open('src/models/train_predictor.py', 'r') as f:
    content = f.read()

# The conversion code to add
conversion_code = """
        # Convert Decimal columns to float
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce')
"""

# Pattern 1: After fetch_stock_data
pattern1 = r'(df = self\.fetch_stock_data\(symbol\))\n'
if re.search(pattern1, content):
    content = re.sub(pattern1, r'\1' + conversion_code + '\n', content)
    print("✓ Fixed fetch_stock_data")

# Pattern 2: After fetch_training_data  
pattern2 = r'(df = self\.fetch_training_data\(symbol\))\n'
if re.search(pattern2, content):
    content = re.sub(pattern2, r'\1' + conversion_code + '\n', content)
    print("✓ Fixed fetch_training_data")

# Pattern 3: Any other df = ... that fetches from database
pattern3 = r'(df = pd\.DataFrame\(prices\))\n'
if re.search(pattern3, content):
    content = re.sub(pattern3, r'\1' + conversion_code + '\n', content)
    print("✓ Fixed DataFrame creation")

# Write back
with open('src/models/train_predictor.py', 'w') as f:
    f.write(content)

print("\n✅ All fixes applied!")
