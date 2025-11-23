"""
ML service for opportunity score prediction
"""
import logging
import os
import pickle
from typing import Optional, Dict, Any
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd

logger = logging.getLogger(__name__)


class MLService:
    """Service for ML-based opportunity score prediction"""
    
    def __init__(self, model_path: str = "ml/model.pkl"):
        """
        Initialize MLService
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path
        self.model: Optional[RandomForestRegressor] = None
        self._load_model()
    
    def _load_model(self):
        """Load saved model from disk"""
        try:
            # Ensure model directory exists
            model_dir = os.path.dirname(self.model_path)
            if model_dir and not os.path.exists(model_dir):
                os.makedirs(model_dir, exist_ok=True)
            
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded model from {self.model_path}")
            else:
                logger.warning(f"Model file not found at {self.model_path}. Using fallback scoring.")
                self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def _fallback_score(self, features: Dict[str, Any]) -> int:
        """
        Fallback rule-based scoring when ML model is not available
        
        Args:
            features: Dictionary with search_trend_score, temperature, rain_probability, is_holiday
        
        Returns:
            Opportunity score (0-100)
        """
        score = 50  # Base score
        
        # Search trend contribution (0-40 points)
        trend_score = features.get("search_trend_score", 50)
        if trend_score is not None:
            score += (trend_score - 50) * 0.4
        
        # Holiday contribution (0-20 points)
        if features.get("is_holiday", False):
            score += 20
        
        # Weather contribution (0-30 points)
        # Higher temperature favors summer products, lower favors winter products
        # This is simplified - in reality, you'd need product-specific logic
        temp = features.get("temperature", 25)
        if temp is not None:
            # Assume moderate temperature is neutral
            if 20 <= temp <= 30:
                score += 10
            elif temp > 30 or temp < 10:
                score += 15  # Extreme weather can drive demand
        
        # Rain probability (negative for most products, positive for rain-related)
        rain_prob = features.get("rain_probability", 0)
        if rain_prob is not None:
            # Simplified: high rain probability reduces score for most products
            # In production, this would be keyword-specific
            score -= rain_prob * 10
        
        # Clamp to 0-100
        score = max(0, min(100, int(score)))
        
        return score
    
    def _generate_explanation(self, features: Dict[str, Any], score: int) -> str:
        """Generate human-readable explanation for the score"""
        explanations = []
        
        trend_score = features.get("search_trend_score")
        if trend_score is not None:
            if trend_score > 70:
                explanations.append("High search interest")
            elif trend_score < 30:
                explanations.append("Low search interest")
            else:
                explanations.append("Moderate search interest")
        
        if features.get("is_holiday", False):
            explanations.append("Holiday/festival period")
        
        temp = features.get("temperature")
        if temp is not None:
            if temp > 35:
                explanations.append("Hot weather expected")
            elif temp < 15:
                explanations.append("Cold weather expected")
        
        rain_prob = features.get("rain_probability", 0)
        if rain_prob is not None:
            if rain_prob > 0.7:
                explanations.append("High rain probability")
            elif rain_prob < 0.3:
                explanations.append("Low rain probability")
        
        if not explanations:
            explanations.append("Baseline conditions")
        
        return ", ".join(explanations)
    
    def predict_opportunity(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict opportunity score for given features
        
        Args:
            features: Dictionary with:
                - search_trend_score: int (0-100)
                - temperature: float
                - rain_probability: float (0-1)
                - is_holiday: bool
        
        Returns:
            Dictionary with opportunity_score, features, and explanation
        """
        try:
            # Prepare feature vector
            feature_vector = np.array([[
                features.get("search_trend_score", 50) or 50,
                features.get("temperature", 25) or 25,
                features.get("rain_probability", 0) or 0,
                1 if features.get("is_holiday", False) else 0
            ]])
            
            # Predict using model if available
            if self.model is not None:
                score = self.model.predict(feature_vector)[0]
                score = max(0, min(100, int(score)))
            else:
                score = self._fallback_score(features)
            
            explanation = self._generate_explanation(features, score)
            
            return {
                "opportunity_score": score,
                "features": features,
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Error predicting opportunity: {e}")
            # Fallback to rule-based scoring
            score = self._fallback_score(features)
            explanation = self._generate_explanation(features, score)
            return {
                "opportunity_score": score,
                "features": features,
                "explanation": explanation
            }

