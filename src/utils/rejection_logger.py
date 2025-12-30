import json
import os
from datetime import datetime
from typing import Dict, Optional

class RejectionLogger:
    """Logger estruturado para registrar rejeições de oportunidades"""
    
    def __init__(self, log_file: str = "logs/rejections.jsonl"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def log_rejection(
        self,
        match: str,
        market: str,
        reason: str,
        details: Dict,
        competition: Optional[str] = None
    ):
        """Registra uma rejeição com detalhes estruturados"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "match": match,
            "market": market,
            "competition": competition,
            "reason": reason,
            "details": details
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
