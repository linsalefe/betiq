import os
import json
from datetime import datetime, date
from typing import Optional, Dict, Any


class DailyCache:
    """Cache que persiste por dia inteiro - busca APIs apenas 1x por dia"""
    
    CACHE_DIR = "cache/daily"
    DATE_FILE = "cache/daily/last_fetch_date.txt"
    DATA_FILE = "cache/daily/opportunities_data.json"
    
    @staticmethod
    def _ensure_cache_dir():
        """Garante que diretório de cache existe"""
        os.makedirs(DailyCache.CACHE_DIR, exist_ok=True)
    
    @staticmethod
    def _get_today() -> str:
        """Retorna data de hoje como string (YYYY-MM-DD)"""
        return date.today().isoformat()
    
    @staticmethod
    def was_fetched_today() -> bool:
        """Verifica se já buscou dados hoje"""
        DailyCache._ensure_cache_dir()
        
        if not os.path.exists(DailyCache.DATE_FILE):
            return False
        
        try:
            with open(DailyCache.DATE_FILE, 'r') as f:
                last_date = f.read().strip()
            
            return last_date == DailyCache._get_today()
        except:
            return False
    
    @staticmethod
    def save_today_data(opportunities: list, matches_count: int, leagues_count: int):
        """Salva dados buscados hoje"""
        DailyCache._ensure_cache_dir()
        
        data = {
            'date': DailyCache._get_today(),
            'timestamp': datetime.now().isoformat(),
            'opportunities': opportunities,
            'matches_count': matches_count,
            'leagues_count': leagues_count
        }
        
        # Salva dados
        with open(DailyCache.DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Marca data de hoje
        with open(DailyCache.DATE_FILE, 'w') as f:
            f.write(DailyCache._get_today())
        
        print(f"✅ Dados salvos no cache diário ({DailyCache._get_today()})")
    
    @staticmethod
    def load_today_data() -> Optional[Dict[str, Any]]:
        """Carrega dados de hoje se existirem"""
        DailyCache._ensure_cache_dir()
        
        if not DailyCache.was_fetched_today():
            return None
        
        try:
            with open(DailyCache.DATA_FILE, 'r') as f:
                data = json.load(f)
            
            print(f"📦 Usando cache diário ({data['date']} às {data['timestamp'][:16]})")
            return data
        except:
            return None
    
    @staticmethod
    def clear_cache():
        """Limpa cache (forçar nova busca)"""
        DailyCache._ensure_cache_dir()
        
        if os.path.exists(DailyCache.DATE_FILE):
            os.remove(DailyCache.DATE_FILE)
        
        if os.path.exists(DailyCache.DATA_FILE):
            os.remove(DailyCache.DATA_FILE)
        
        print("🗑️  Cache diário limpo!")