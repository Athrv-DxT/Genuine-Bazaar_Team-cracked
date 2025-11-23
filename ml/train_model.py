"""
Train ML model for opportunity score prediction
"""
import sys
import os
import logging
import pickle
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models import SignalSnapshot, OpportunityLabel
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_synthetic_labels():
    """
    Generate synthetic opportunity labels if real labels are not available.
    This creates labels based on a simple rule-based function.
    """
    logger.info("Generating synthetic opportunity labels...")
    
    # Get all snapshots
    snapshots = db.session.query(SignalSnapshot).all()
    
    labels_created = 0
    for snapshot in snapshots:
        # Check if label already exists
        existing = db.session.query(OpportunityLabel)\
            .filter(OpportunityLabel.city == snapshot.city)\
            .filter(OpportunityLabel.keyword == snapshot.keyword)\
            .filter(OpportunityLabel.timestamp == snapshot.timestamp)\
            .first()
        
        if existing:
            continue
        
        # Generate synthetic label based on features
        score = 50  # Base score
        
        # Search trend contribution
        if snapshot.search_trend_score:
            score += (snapshot.search_trend_score - 50) * 0.4
        
        # Holiday contribution
        if snapshot.is_holiday:
            score += 20
        
        # Temperature contribution (simplified)
        if snapshot.temperature:
            if 20 <= snapshot.temperature <= 30:
                score += 10
            elif snapshot.temperature > 30 or snapshot.temperature < 10:
                score += 15
        
        # Rain probability (negative for most products)
        if snapshot.rain_probability:
            score -= snapshot.rain_probability * 10
        
        # Clamp to 0-100
        score = max(0, min(100, int(score)))
        
        # Create label
        label = OpportunityLabel(
            timestamp=snapshot.timestamp,
            city=snapshot.city,
            keyword=snapshot.keyword,
            label_score=score,
            snapshot_id=snapshot.id
        )
        db.session.add(label)
        labels_created += 1
    
    db.session.commit()
    logger.info(f"Created {labels_created} synthetic labels")


def train_model():
    """Train the ML model"""
    app = create_app()
    
    with app.app_context():
        # Check if we have labels
        label_count = db.session.query(OpportunityLabel).count()
        
        if label_count == 0:
            logger.info("No labels found. Generating synthetic labels...")
            generate_synthetic_labels()
            label_count = db.session.query(OpportunityLabel).count()
        
        if label_count < 10:
            logger.warning(f"Only {label_count} labels available. Model may not be accurate.")
        
        # Join snapshots with labels
        query = db.session.query(
            SignalSnapshot.search_trend_score,
            SignalSnapshot.temperature,
            SignalSnapshot.rain_probability,
            SignalSnapshot.is_holiday,
            OpportunityLabel.label_score
        ).join(
            OpportunityLabel,
            OpportunityLabel.snapshot_id == SignalSnapshot.id
        )
        
        # Convert to DataFrame
        data = pd.read_sql(query.statement, db.session.bind)
        
        if data.empty:
            logger.error("No training data available. Please run fetch_signals first.")
            return
        
        # Prepare features and target
        feature_cols = ['search_trend_score', 'temperature', 'rain_probability', 'is_holiday']
        X = data[feature_cols].fillna(0)
        y = data['label_score']
        
        # Handle missing values
        X = X.replace([np.inf, -np.inf], 0)
        
        # Split data
        if len(X) > 1:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y, y
        
        # Train model
        logger.info(f"Training model with {len(X_train)} samples...")
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        if len(X_test) > 0:
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            logger.info(f"Model performance - MSE: {mse:.2f}, R²: {r2:.2f}")
        
        # Save model
        model_dir = Path(__file__).parent
        model_dir.mkdir(exist_ok=True)
        model_path = model_dir / "model.pkl"
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Model saved to {model_path}")
        
        # Print feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Feature importance:")
        for _, row in feature_importance.iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.3f}")


if __name__ == "__main__":
    train_model()

