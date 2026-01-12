"""
Sentiment Analysis Model
Fine-tuned DistilBERT for financial sentiment analysis
"""

import torch
import torch.nn as nn
from transformers import (
    DistilBertTokenizer, 
    DistilBertForSequenceClassification,
    AdamW,
    get_linear_schedule_with_warmup
)
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import logging
from tqdm import tqdm
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database.db_manager import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialSentimentDataset(Dataset):
    """PyTorch Dataset for financial sentiment analysis."""
    
    def __init__(
        self, 
        texts: List[str], 
        labels: Optional[List[int]] = None,
        tokenizer: DistilBertTokenizer = None,
        max_length: int = 128
    ):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer or DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        item = {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten()
        }
        
        if self.labels is not None:
            item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        
        return item


class SentimentAnalyzer:
    """
    Financial sentiment analysis using fine-tuned DistilBERT.
    Classifies text as positive (1), neutral (0), or negative (-1).
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize sentiment analyzer.
        
        Args:
            model_path: Path to saved model weights
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        
        # Load model
        if model_path and Path(model_path).exists():
            self.model = self._load_model(model_path)
        else:
            self.model = DistilBertForSequenceClassification.from_pretrained(
                'distilbert-base-uncased',
                num_labels=3  # negative, neutral, positive
            )
        
        self.model.to(self.device)
        self.label_map = {0: -1, 1: 0, 2: 1}  # Map to sentiment scores
        self.db = get_db_manager()
    
    def _load_model(self, model_path: str):
        """Load saved model weights."""
        model = DistilBertForSequenceClassification.from_pretrained(
            'distilbert-base-uncased',
            num_labels=3
        )
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        logger.info(f"Loaded model from {model_path}")
        return model
    
    def prepare_training_data(self) -> Tuple[List[str], List[int]]:
        """
        Prepare training data from database or use sample data.
        In production, this would load labeled financial news.
        """
        # Sample financial sentiment data for demonstration
        # In production, replace with real labeled data
        texts = [
            "Company reports record profits beating analyst expectations",
            "Stock price surges on positive earnings report",
            "Market volatility continues amid economic uncertainty",
            "Company faces regulatory challenges and declining sales",
            "Investors remain cautious ahead of earnings announcement",
            "Strong growth in revenue and expanding market share",
            "Disappointing quarter results lead to stock decline",
            "Analyst upgrades stock rating citing strong fundamentals",
            "Concerns over supply chain disruptions impact sentiment",
            "Company announces strategic partnership with industry leader"
        ]
        
        # Labels: 0=negative, 1=neutral, 2=positive
        labels = [2, 2, 1, 0, 1, 2, 0, 2, 0, 2]
        
        logger.info(f"Prepared {len(texts)} training samples")
        return texts, labels
    
    def train(
        self, 
        texts: List[str], 
        labels: List[int],
        epochs: int = 3,
        batch_size: int = 8,
        learning_rate: float = 2e-5,
        val_split: float = 0.2
    ) -> Dict[str, float]:
        """
        Train the sentiment analysis model.
        
        Args:
            texts: Training texts
            labels: Training labels (0=negative, 1=neutral, 2=positive)
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            val_split: Validation split ratio
            
        Returns:
            Dictionary with training metrics
        """
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=val_split, random_state=42, stratify=labels
        )
        
        # Create datasets
        train_dataset = FinancialSentimentDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = FinancialSentimentDataset(val_texts, val_labels, self.tokenizer)
        
        # Create dataloaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Optimizer and scheduler
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        # Training loop
        self.model.train()
        best_val_accuracy = 0
        
        for epoch in range(epochs):
            logger.info(f"Epoch {epoch + 1}/{epochs}")
            
            total_loss = 0
            for batch in tqdm(train_loader, desc="Training"):
                # Move to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels_batch = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels_batch
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
            
            avg_loss = total_loss / len(train_loader)
            
            # Validation
            val_accuracy, val_metrics = self._evaluate(val_loader)
            
            logger.info(f"Train Loss: {avg_loss:.4f}, Val Accuracy: {val_accuracy:.4f}")
            
            # Save best model
            if val_accuracy > best_val_accuracy:
                best_val_accuracy = val_accuracy
                self._save_model("models/sentiment_model_best.pth")
        
        return {
            'final_train_loss': avg_loss,
            'best_val_accuracy': best_val_accuracy,
            **val_metrics
        }
    
    def _evaluate(self, dataloader: DataLoader) -> Tuple[float, Dict[str, float]]:
        """Evaluate model on validation/test set."""
        self.model.eval()
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels_batch = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                preds = torch.argmax(logits, dim=1)
                
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels_batch.cpu().numpy())
        
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='weighted'
        )
        
        self.model.train()
        
        return accuracy, {
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def predict_sentiment(
        self, 
        texts: List[str]
    ) -> List[Dict[str, float]]:
        """
        Predict sentiment for a list of texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of dicts with sentiment_score and confidence
        """
        self.model.eval()
        
        dataset = FinancialSentimentDataset(texts, tokenizer=self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=8)
        
        results = []
        
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                
                # Get probabilities
                probs = torch.softmax(logits, dim=1)
                predictions = torch.argmax(probs, dim=1)
                confidences = torch.max(probs, dim=1).values
                
                # Convert to sentiment scores
                for pred, conf in zip(predictions.cpu().numpy(), confidences.cpu().numpy()):
                    results.append({
                        'sentiment_score': self.label_map[pred],
                        'confidence': float(conf),
                        'label': ['negative', 'neutral', 'positive'][pred]
                    })
        
        return results
    
    def analyze_news_in_db(self, limit: Optional[int] = None):
        """
        Analyze sentiment for news articles in database.
        
        Args:
            limit: Maximum number of articles to process
        """
        # Fetch articles without sentiment
        query = """
            SELECT article_id, stock_id, title, description 
            FROM news_articles 
            WHERE sentiment_score IS NULL
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        articles = self.db.fetch_dict(query)
        
        if not articles:
            logger.info("No articles to analyze")
            return
        
        logger.info(f"Analyzing {len(articles)} articles...")
        
        # Prepare texts (combine title and description)
        texts = [
            f"{a['title']} {a['description'] or ''}"
            for a in articles
        ]
        
        # Predict sentiments
        sentiments = self.predict_sentiment(texts)
        
        # Update database
        update_query = """
            UPDATE news_articles 
            SET sentiment_score = %s, 
                sentiment_label = %s, 
                confidence = %s,
                model_version = 'distilbert-v1'
            WHERE article_id = %s
        """
        
        data = [
            (
                s['sentiment_score'],
                s['label'],
                s['confidence'],
                articles[i]['article_id']
            )
            for i, s in enumerate(sentiments)
        ]
        
        self.db.execute_many(update_query, data)
        logger.info(f"Updated sentiment for {len(data)} articles")
    
    def _save_model(self, path: str):
        """Save model weights."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)
        logger.info(f"Model saved to {path}")


def main():
    """Main training function."""
    analyzer = SentimentAnalyzer()
    
    # Prepare training data
    texts, labels = analyzer.prepare_training_data()
    
    # Train model
    logger.info("Starting training...")
    metrics = analyzer.train(texts, labels, epochs=3)
    
    logger.info("Training complete!")
    logger.info(f"Metrics: {metrics}")
    
    # Test predictions
    test_texts = [
        "Company announces strong quarterly earnings",
        "Stock price drops on disappointing guidance"
    ]
    
    predictions = analyzer.predict_sentiment(test_texts)
    
    for text, pred in zip(test_texts, predictions):
        logger.info(f"Text: {text}")
        logger.info(f"Sentiment: {pred['label']} (score: {pred['sentiment_score']}, confidence: {pred['confidence']:.3f})")


if __name__ == "__main__":
    main()