#!/usr/bin/env python3

# Read the file
with open('src/models/train_predictor.py', 'r') as f:
    content = f.read()

# Remove everything after "def main():" if it exists
if 'def main():' in content:
    # Split at the first occurrence of def main():
    before_main = content.split('def main():', 1)[0]
else:
    before_main = content

# Add the correct main function
new_main = '''
def main():
    import sys
    
    # Get symbol from command line
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
        print(f"\\n>>> Training {symbol} <<<\\n")
    else:
        symbol = 'AAPL'
        print(f"\\n>>> No symbol provided, training AAPL <<<\\n")
    
    logger.info(f"Training price prediction model for {symbol}...")
    
    # Train
    predictor = StockPredictor(symbol)
    metrics = predictor.train()
    
    # Predict
    prediction = predictor.predict(symbol)
    
    # Display results
    logger.info(f"\\n" + "="*50)
    logger.info(f"Prediction for {symbol}:")
    logger.info(f"Current Price: ${prediction['current_price']:.2f}")
    logger.info(f"Predicted Price: ${prediction['predicted_price']:.2f}")
    logger.info(f"Confidence Interval: ${prediction['confidence_lower']:.2f} - ${prediction['confidence_upper']:.2f}")
    logger.info("="*50)


if __name__ == "__main__":
    main()
'''

# Write the new file
with open('src/models/train_predictor.py', 'w') as f:
    f.write(before_main)
    f.write(new_main)

print("✓ File fixed with new main function!")
