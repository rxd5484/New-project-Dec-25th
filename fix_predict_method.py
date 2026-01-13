import re

# Read file
with open('src/models/train_predictor.py', 'r') as f:
    content = f.read()

# Find the predict method and add conversion after df = self.fetch_stock_data(symbol)
pattern = r'(def predict\(self, symbol: str\) -> Dict:.*?df = self\.fetch_stock_data\(symbol\))'
replacement = r'\1\n        \n        # Convert Decimal columns to float\n        for col in df.columns:\n            if df[col].dtype == \'object\':\n                df[col] = pd.to_numeric(df[col], errors=\'coerce\')'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('src/models/train_predictor.py', 'w') as f:
    f.write(content)

print("✓ Fixed predict method!")
