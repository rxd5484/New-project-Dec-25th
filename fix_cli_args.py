#!/usr/bin/env python3
"""Fix command-line argument handling"""

# Read the file
with open('src/models/train_predictor.py', 'r') as f:
    lines = f.readlines()

# Find and replace the main function
new_lines = []
in_main = False
main_replaced = False

for i, line in enumerate(lines):
    if 'def main():' in line and not main_replaced:
        # Replace the entire main function
        new_lines.append(line)
        new_lines.append('    import sys\n')
        new_lines.append('    \n')
        new_lines.append('    # Get symbol from command line or use default\n')
        new_lines.append('    if len(sys.argv) > 1:\n')
        new_lines.append('        symbols = [sys.argv[1].upper()]\n')
        new_lines.append('    else:\n')
        new_lines.append('        symbols = [\'AAPL\']\n')
        new_lines.append('    \n')
        in_main = True
        main_replaced = True
    elif in_main and "symbols = ['AAPL']" in line:
        # Skip the old hardcoded line
        continue
    else:
        new_lines.append(line)

# Write back
with open('src/models/train_predictor.py', 'w') as f:
    f.writelines(new_lines)

print("✓ Fixed command-line argument handling!")
