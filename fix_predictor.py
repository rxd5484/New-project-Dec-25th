import sys
from pathlib import Path

# Read the file
file_path = Path('src/models/train_predictor.py')
content = file_path.read_text()

# Fix 1: Replace deprecated fillna
content = content.replace(
    "df = df.fillna(method='ffill').fillna(0)",
    "df = df.ffill().fillna(0)"
)

# Fix 2: Add decimal to float conversion after data fetch
# Find the line with "Fetched" and add conversion after it
import_section = """import torch
import torch.nn as nn
import numpy as np
import pandas as pd"""

new_import = """import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from decimal import Decimal"""

content = content.replace(import_section, new_import)

# Add conversion function
conversion_func = """
def convert_decimals_to_float(df):
    '''Convert Decimal columns to float'''
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = df[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)
            except:
                pass
    return df
"""

# Insert after imports
lines = content.split('\n')
import_end = 0
for i, line in enumerate(lines):
    if line.startswith('from') or line.startswith('import'):
        import_end = i
        
lines.insert(import_end + 2, conversion_func)
content = '\n'.join(lines)

# Add conversion call after DataFrame creation
content = content.replace(
    "df = pd.DataFrame(prices)",
    "df = pd.DataFrame(prices)\n        df = convert_decimals_to_float(df)"
)

# Write back
file_path.write_text(content)
print("✓ Fixed train_predictor.py")
