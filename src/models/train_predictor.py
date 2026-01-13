"""
Stock Price Prediction Model
LSTM with attention mechanism for next-day price prediction
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from decimal import Decimal
from typing import Tuple, List, Dict, Optional
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
from pathlib import Path
import sys
import joblib

sys.path.append(str(Path(__file__).parent.parent))
from database.db_manager import get_db_manager


def convert_decimals_to_float(df):
    '''Convert Decimal columns to float'''
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = df[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)
            except:
                pass
    return df

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttentionLSTM(nn.Module):
    """LSTM with attention mechanism for time series prediction."""
    
    def __init__(
        self, 
        input_size: int, 
        hidden_size: int = 128, 
        num_layers: int = 2,
        dropout: float = 0.2
    ):
        super(AttentionLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention mechanism
        self.attention = nn.Linear(hidden_size, 1)
        
        # Output layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(64, 1)
        
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden_size)
        
        # Attention weights
        attention_weights = torch.softmax(self.attention(lstm_out), dim=1)
        
        # Apply attention
        context = torch.sum(attention_weights * lstm_out, dim=1)
        
        # Fully connected layers
        out = self.relu(self.fc1(context))
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out


class StockPricePredictor:
    """
    Stock price prediction using LSTM with attention.
    Predicts next-day closing price based on historical data and sentiment.
    """
    
    def __init__(
        self, 
        sequence_length: int = 60,
        model_path: Optional[str] = None
    ):
        """
        Initialize predictor.
        
        Args:
            sequence_length: Number of days to use for prediction
            model_path: Path to saved model
        """
        self.sequence_length = sequence_length
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.db = get_db_manager()
        
        self.scaler_features = MinMaxScaler()
        self.scaler_target = MinMaxScaler()
        
        self.model = None
        self.feature_columns = [
            'open_price', 'high_price', 'low_price', 'close_price', 'volume',
            'sma_20', 'sma_50', 'ema_12', 'ema_26', 'rsi', 
            'macd', 'macd_signal', 'sentiment_score'
        ]
        
        if model_path and Path(model_path).exists():
            self._load_model(model_path)
    
    def fetch_training_data(
        self, 
        symbol: str,
        include_sentiment: bool = True
    ) -> pd.DataFrame:
        """
        Fetch training data from database.
        
        Args:
            symbol: Stock symbol
            include_sentiment: Whether to include sentiment data
            
        Returns:
            DataFrame with features
        """
        # Base query for stock prices
        query = """
            SELECT 
                sp.price_date,
                sp.open_price,
                sp.high_price,
                sp.low_price,
                sp.close_price,
                sp.volume,
                sp.sma_20,
                sp.sma_50,
                sp.ema_12,
                sp.ema_26,
                sp.rsi,
                sp.macd,
                sp.macd_signal
        """
        
        if include_sentiment:
            query += """
                ,COALESCE(
                    (SELECT AVG(sentiment_score) 
                     FROM news_articles na 
                     WHERE na.stock_id = s.stock_id 
                     AND DATE(na.published_at) = sp.price_date),
                    0
                ) as sentiment_score
            """
        
        query += """
            FROM stocks s
            JOIN stock_prices sp ON s.stock_id = sp.stock_id
            WHERE s.symbol = %s
            ORDER BY sp.price_date ASC
        """
        
        df = pd.DataFrame(self.db.fetch_dict(query, (symbol,)))
        
        if df.empty:
            logger.warning(f"No data found for {symbol}")
            return df
        
        # Add sentiment column if not included in query
        if not include_sentiment:
            df['sentiment_score'] = 0
        
        # Fill missing values
        df = df.ffill().fillna(0)
        
        logger.info(f"Fetched {len(df)} records for {symbol}")
        return df
    
    def prepare_sequences(
        self, 
        df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for LSTM training.
        
        Args:
            df: DataFrame with features
            
        Returns:
            Tuple of (X, y) arrays
        """
        # Select features
        features = df[self.feature_columns].values
        target = df['close_price'].values.reshape(-1, 1)
        
        # Scale features
        features_scaled = self.scaler_features.fit_transform(features)
        target_scaled = self.scaler_target.fit_transform(target)
        
        # Create sequences
        X, y = [], []
        
        for i in range(self.sequence_length, len(features_scaled)):
            X.append(features_scaled[i-self.sequence_length:i])
            y.append(target_scaled[i])
        
        return np.array(X), np.array(y)
    
    def train(
        self,
        symbol: str,
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        val_split: float = 0.2
    ) -> Dict[str, float]:
        """
        Train the LSTM model.
        
        Args:
            symbol: Stock symbol
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            val_split: Validation split ratio
            
        Returns:
            Dictionary with training metrics
        """
        # Fetch data
        df = self.fetch_training_data(symbol)
        # Convert Decimal columns to float
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce')

        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Prepare sequences
        X, y = self.prepare_sequences(df)
        
        # Split data
        split_idx = int(len(X) * (1 - val_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Convert to tensors
        X_train = torch.FloatTensor(X_train).to(self.device)
        y_train = torch.FloatTensor(y_train).to(self.device)
        X_val = torch.FloatTensor(X_val).to(self.device)
        y_val = torch.FloatTensor(y_val).to(self.device)
        
        # Initialize model
        input_size = X_train.shape[2]
        self.model = AttentionLSTM(
            input_size=input_size,
            hidden_size=128,
            num_layers=2,
            dropout=0.2
        ).to(self.device)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5
        )
        
        # Training loop
        best_val_loss = float('inf')
        train_losses = []
        val_losses = []
        
        logger.info(f"Training model for {symbol}...")
        
        for epoch in range(epochs):
            self.model.train()
            
            # Mini-batch training
            total_loss = 0
            num_batches = len(X_train) // batch_size
            
            for i in range(num_batches):
                start_idx = i * batch_size
                end_idx = start_idx + batch_size
                
                batch_X = X_train[start_idx:end_idx]
                batch_y = y_train[start_idx:end_idx]
                
                # Forward pass
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_train_loss = total_loss / num_batches
            train_losses.append(avg_train_loss)
            
            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val)
                val_loss = criterion(val_outputs, y_val).item()
                val_losses.append(val_loss)
            
            scheduler.step(val_loss)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {avg_train_loss:.6f}, Val Loss: {val_loss:.6f}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self._save_model(f"models/{symbol}_price_model.pth")
        
        # Calculate metrics
        metrics = self._calculate_metrics(X_val, y_val)
        
        return {
            'final_train_loss': train_losses[-1],
            'best_val_loss': best_val_loss,
            **metrics
        }
    
    def _calculate_metrics(
        self, 
        X: torch.Tensor, 
        y_true: torch.Tensor
    ) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        self.model.eval()
        
        with torch.no_grad():
            y_pred = self.model(X).cpu().numpy()
        
        y_true = y_true.cpu().numpy()
        
        # Inverse transform
        y_true_actual = self.scaler_target.inverse_transform(y_true)
        y_pred_actual = self.scaler_target.inverse_transform(y_pred)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_true_actual, y_pred_actual))
        mae = mean_absolute_error(y_true_actual, y_pred_actual)
        r2 = r2_score(y_true_actual, y_pred_actual)
        
        # Directional accuracy
        direction_actual = np.diff(y_true_actual.flatten()) > 0
        direction_pred = np.diff(y_pred_actual.flatten()) > 0
        directional_accuracy = np.mean(direction_actual == direction_pred)
        
        return {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'directional_accuracy': float(directional_accuracy)
        }
    
    def predict(
        self, 
        symbol: str, 
        days_ahead: int = 1
    ) -> Dict[str, float]:
        """
        Predict future stock price.
        
        Args:
            symbol: Stock symbol
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dictionary with prediction and confidence interval
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Fetch recent data
        df = self.fetch_training_data(symbol)
        # Convert Decimal columns to float
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce')

        
        if len(df) < self.sequence_length:
            raise ValueError(f"Not enough data for prediction")
        
        # Get last sequence
        features = df[self.feature_columns].values
        features_scaled = self.scaler_features.transform(features)
        
        last_sequence = features_scaled[-self.sequence_length:]
        X = torch.FloatTensor(last_sequence).unsqueeze(0).to(self.device)
        
        # Predict
        self.model.eval()
        with torch.no_grad():
            prediction_scaled = self.model(X).cpu().numpy()
        
        # Inverse transform
        prediction = self.scaler_target.inverse_transform(prediction_scaled)[0][0]
        
        # Calculate confidence interval (simplified)
        std = df['close_price'].std()
        confidence_lower = prediction - 1.96 * std
        confidence_upper = prediction + 1.96 * std
        
        return {
            'predicted_price': float(prediction),
            'confidence_lower': float(confidence_lower),
            'confidence_upper': float(confidence_upper),
            'current_price': float(df['close_price'].iloc[-1])
        }
    
    def _save_model(self, path: str):
        """Save model and scalers."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save model
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'scaler_features': self.scaler_features,
            'scaler_target': self.scaler_target,
            'feature_columns': self.feature_columns
        }, path)
        
        logger.info(f"Model saved to {path}")
    
    def _load_model(self, path: str):
        """Load model and scalers."""
        checkpoint = torch.load(path, map_location=self.device)
        
        # Restore scalers
        self.scaler_features = checkpoint['scaler_features']
        self.scaler_target = checkpoint['scaler_target']
        self.feature_columns = checkpoint['feature_columns']
        
        # Initialize and load model
        input_size = len(self.feature_columns)
        self.model = AttentionLSTM(input_size=input_size).to(self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        logger.info(f"Model loaded from {path}")



def main():
    import sys
    
    # Get symbol from command line
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
        print(f"\n>>> Training {symbol} <<<\n")
    else:
        symbol = 'AAPL'
        print(f"\n>>> No symbol provided, training AAPL <<<\n")
    
    logger.info(f"Training price prediction model for {symbol}...")
    
    # Train
    predictor = StockPricePredictor()
    metrics = predictor.train(symbol)
    
    # Predict
    prediction = predictor.predict(symbol)
    
    # Display results
    logger.info(f"\n" + "="*50)
    logger.info(f"Prediction for {symbol}:")
    logger.info(f"Current Price: ${prediction['current_price']:.2f}")
    logger.info(f"Predicted Price: ${prediction['predicted_price']:.2f}")
    logger.info(f"Confidence Interval: ${prediction['confidence_lower']:.2f} - ${prediction['confidence_upper']:.2f}")
    logger.info("="*50)


if __name__ == "__main__":
    main()
