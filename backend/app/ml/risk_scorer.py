"""
Machine Learning Risk Scoring Engine
Uses XGBoost for malware classification
"""

import joblib
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
import os

logger = logging.getLogger(__name__)


class RiskScorer:
    """ML-based risk scoring using XGBoost"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.getenv("XGBOOST_MODEL_PATH", "./models/risk_scorer.pkl")
        self.model = None
        self._load_model()
        
        # Feature weights for manual scoring
        self.feature_weights = {
            "permissions": 0.25,
            "network_activity": 0.20,
            "suspicious_apis": 0.20,
            "c2_indicators": 0.15,
            "encryption": 0.10,
            "obfuscation": 0.10,
        }

    def _load_model(self) -> None:
        """Load pre-trained XGBoost model"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded model from {self.model_path}")
            else:
                logger.warning(f"Model not found at {self.model_path}, using fallback scoring")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")

    def calculate_risk_score(self, analysis_data: Dict[str, Any]) -> Tuple[float, str]:
        """
        Calculate risk score using ML model or fallback method
        Returns: (score: 0-100, risk_level: critical/high/medium/low)
        """
        try:
            if self.model:
                return self._ml_score(analysis_data)
            else:
                return self._fallback_score(analysis_data)
        except Exception as e:
            logger.error(f"Risk scoring failed: {str(e)}")
            return 50.0, "unknown"

    def _ml_score(self, analysis_data: Dict[str, Any]) -> Tuple[float, str]:
        """Use ML model for scoring"""
        try:
            features = self._extract_features(analysis_data)
            features_array = np.array([features])
            
            # Get prediction probability
            prediction = self.model.predict_proba(features_array)
            malware_probability = prediction[0][1]  # Probability of malware class
            
            score = malware_probability * 100
            risk_level = self._score_to_risk_level(score)
            
            return score, risk_level
        except Exception as e:
            logger.error(f"ML scoring failed: {str(e)}")
            return 50.0, "unknown"

    def _fallback_score(self, analysis_data: Dict[str, Any]) -> Tuple[float, str]:
        """Fallback heuristic-based scoring"""
        score = 0.0
        perms = analysis_data.get("permissions") or []
        if not isinstance(perms, list):
            perms = []
        network = analysis_data.get("network_traffic") or []
        if not isinstance(network, list):
            network = []
        urls = analysis_data.get("urls") or []
        domains = analysis_data.get("domains") or []
        c2 = analysis_data.get("c2_communications") or []
        apis = analysis_data.get("suspicious_apis") or []
        if isinstance(apis, dict):
            apis = [k for k, v in apis.items() if v]

        permissions_risk = self._analyze_permissions(perms)
        score += permissions_risk * self.feature_weights["permissions"]

        network_risk = self._analyze_network_activity(network, urls, domains, c2)
        score += network_risk * self.feature_weights["network_activity"]

        api_risk = self._analyze_apis(apis)
        score += api_risk * self.feature_weights["suspicious_apis"]
        
        # C2 Indicators
        c2_risk = min(len(c2) * 0.2, 1.0)
        score += c2_risk * self.feature_weights["c2_indicators"]
        
        # Encryption
        secrets = analysis_data.get("hardcoded_secrets") or []
        if not isinstance(secrets, list):
            secrets = []
        encryption_risk = self._analyze_encryption(secrets)
        score += encryption_risk * self.feature_weights["encryption"]
        
        # Obfuscation
        obfuscation_risk = self._analyze_obfuscation(analysis_data)
        score += obfuscation_risk * self.feature_weights["obfuscation"]
        
        risk_level = self._score_to_risk_level(score * 100)
        return score * 100, risk_level

    def _analyze_permissions(self, permissions: List[str]) -> float:
        """Analyze permissions for risk"""
        dangerous_perms = {
            "RECORD_AUDIO", "CAMERA", "ACCESS_FINE_LOCATION",
            "READ_CONTACTS", "READ_SMS", "SEND_SMS", "CALL_PHONE"
        }
        
        risk = 0.0
        for perm in permissions:
            perm_name = perm.split(".")[-1]
            if perm_name in dangerous_perms:
                risk += 0.15
        
        return min(risk, 1.0)

    def _analyze_network_activity(self, network_traffic: List[Dict], urls: List[str],
                                 domains: List[str], c2_communications: List[Dict]) -> float:
        """Analyze network activity for risk"""
        risk = 0.0
        
        # High number of connections is suspicious
        risk += min(len(network_traffic) * 0.02, 0.3)
        
        # URLs and domains
        risk += min(len(urls) * 0.05, 0.2)
        risk += min(len(domains) * 0.03, 0.2)
        
        # C2 communications
        risk += min(len(c2_communications) * 0.2, 0.5)
        
        return min(risk, 1.0)

    def _analyze_apis(self, apis: List[str]) -> float:
        """Analyze suspicious API usage"""
        # Rough estimate based on number of suspicious APIs
        risk = min(len(apis) * 0.05, 1.0)
        return risk

    def _analyze_encryption(self, secrets: List[Dict]) -> float:
        """Analyze encryption and hardcoded secrets"""
        risk = min(len(secrets) * 0.2, 1.0)
        return risk

    def _analyze_obfuscation(self, analysis_data: Dict[str, Any]) -> float:
        """Detect code obfuscation"""
        # Check for suspicious patterns indicating obfuscation
        risk = 0.0
        
        # If manifest is very large or has unusual patterns
        manifest_len = len(str(analysis_data.get("manifest", "")))
        if manifest_len > 10000:
            risk += 0.2
        
        return min(risk, 1.0)

    def _extract_features(self, analysis_data: Dict[str, Any]) -> List[float]:
        """Extract features for ML model"""
        features = []
        
        # Count-based features
        features.append(len(analysis_data.get("permissions", [])))
        features.append(len(analysis_data.get("activities", [])))
        features.append(len(analysis_data.get("services", [])))
        features.append(len(analysis_data.get("broadcast_receivers", [])))
        features.append(len(analysis_data.get("content_providers", [])))
        features.append(len(analysis_data.get("urls", [])))
        features.append(len(analysis_data.get("ips", [])))
        features.append(len(analysis_data.get("domains", [])))
        features.append(len(analysis_data.get("network_traffic", [])))
        features.append(len(analysis_data.get("c2_communications", [])))
        features.append(len(analysis_data.get("suspicious_apis", [])))
        features.append(len(analysis_data.get("hardcoded_secrets", [])))
        
        # Binary features
        features.append(1.0 if analysis_data.get("has_native_code") else 0.0)
        features.append(1.0 if analysis_data.get("is_obfuscated") else 0.0)
        
        return features

    @staticmethod
    def _score_to_risk_level(score: float) -> str:
        """Convert numerical score to risk level"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        elif score >= 20:
            return "low"
        else:
            return "benign"


class MalwareClassifier:
    """Classify types of malware"""
    
    MALWARE_TYPES = {
        "trojan": ["banking", "spy", "generic"],
        "adware": ["aggressive", "generic"],
        "pua": ["potentially_unwanted"],
        "ransomware": ["crypto", "generic"],
        "worm": ["network", "generic"],
        "rootkit": ["privilege_escalation"],
        "spyware": ["data_collection", "tracking"],
    }
    
    @staticmethod
    def classify(analysis_data: Dict[str, Any]) -> List[Dict]:
        """Classify malware types"""
        classifications = []
        
        # Analyze indicators
        c2_count = len(analysis_data.get("c2_communications", []))
        api_calls = analysis_data.get("suspicious_apis", [])
        
        if c2_count > 0:
            classifications.append({
                "type": "trojan",
                "subtype": "command_control",
                "confidence": 0.8
            })
        
        if "RECORD_AUDIO" in str(api_calls) or "CAMERA" in str(api_calls):
            classifications.append({
                "type": "spyware",
                "subtype": "surveillance",
                "confidence": 0.7
            })
        
        if "SEND_SMS" in str(api_calls):
            classifications.append({
                "type": "trojan",
                "subtype": "premium_sms",
                "confidence": 0.7
            })
        
        return classifications if classifications else [
            {"type": "unknown", "confidence": 0.0}
        ]
