"""
ML Model Service - Loads and uses trained models
"""
import torch
import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

# Try to import the predictor
try:
    from src.models.train_predictor import StockPricePredictor
    MODELS_AVAILABLE = True
    logger.info("✓ ML models module loaded successfully")
except Exception as e:
    MODELS_AVAILABLE = False
    logger.warning(f"⚠ ML models not available: {e}")


class MLPredictionService:
    """Service to manage ML model predictions"""
    
    def __init__(self):
        self.models = {}
        self.symbols = ['AAPL', 'TSLA', 'AMZN', 'NVDA', 'GOOGL', 'MSFT']
        self.models_dir = Path(__file__).parent.parent.parent / 'models'
        
        if MODELS_AVAILABLE:
            self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        logger.info("Loading trained models...")
        
        for symbol in self.symbols:
            model_path = self.models_dir / f'{symbol}_price_model.pth'
            
            if model_path.exists():
                try:
                    # Initialize predictor with model path
                    predictor = StockPricePredictor(
                        sequence_length=60,
                        model_path=str(model_path)
                    )
                    self.models[symbol] = predictor
                    logger.info(f"✓ Loaded model for {symbol}")
                except Exception as e:
                    logger.error(f"✗ Failed to load {symbol}: {e}")
            else:
                logger.warning(f"⚠ Model file not found: {model_path}")
        
        logger.info(f"Loaded {len(self.models)}/{len(self.symbols)} models")
    
    def get_prediction(self, symbol: str):
        """Get prediction from trained model"""
        if not MODELS_AVAILABLE:
            logger.warning("Models not available, returning None")
            return None
        
        if symbol not in self.models:
            logger.warning(f"Model not loaded for {symbol}")
            return None
        
        try:
            predictor = self.models[symbol]
            prediction = predictor.predict(symbol)
            logger.info(f"✓ Generated prediction for {symbol}")
            return prediction
        except Exception as e:
            logger.error(f"Prediction error for {symbol}: {e}")
            return None
    
    def is_model_loaded(self, symbol: str) -> bool:
        """Check if model is loaded for symbol"""
        return symbol in self.models


# Global instance
ml_service = MLPredictionService()
