import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import traceback

logger = logging.getLogger(__name__)

class MatchbookService:
    """Serviço para integração com a API da Matchbook"""
    
    def __init__(self):
        self.base_url = os.getenv('MATCHBOOK_BASE_URL', 'https://api.matchbook.com')
        self.username = os.getenv('MATCHBOOK_USERNAME')
        self.password = os.getenv('MATCHBOOK_PASSWORD')
        self.session_token = None
        self.session_expiry = None
        
    def _get_headers(self, include_auth: bool = False) -> Dict[str, str]:
        """Retorna headers para requisições"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        if include_auth and self.session_token:
            headers['session-token'] = self.session_token
            
        return headers
    
    def login(self) -> bool:
        """Faz login na Matchbook e obtém session token"""
        try:
            if self.session_token and self.session_expiry:
                if datetime.now() < self.session_expiry:
                    logger.info("Sessão Matchbook ainda válida")
                    return True
            
            url = f"{self.base_url}/bpapi/rest/security/session"
            payload = {
                "username": self.username,
                "password": self.password
            }
            
            print(f"DEBUG: URL = {url}")
            
            # Tenta com timeout maior
            response = requests.post(
                url, 
                json=payload, 
                headers=self._get_headers(),
                timeout=30
            )
            
            print(f"DEBUG: Status = {response.status_code}")
            print(f"DEBUG: Content-Type = {response.headers.get('Content-Type')}")
            
            # Se retornou HTML, a API não está acessível
            if 'text/html' in response.headers.get('Content-Type', ''):
                print("❌ API retornou HTML. Possíveis causas:")
                print("   1. Cloudflare bloqueando requisições do Brasil")
                print("   2. API indisponível na sua região")
                print("   3. Precisa acessar via VPN")
                return False
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('session-token')
                self.session_expiry = datetime.now() + timedelta(hours=5, minutes=45)
                print("✅ Login realizado!")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def get_sports(self) -> Optional[List[Dict]]:
        """Busca lista de esportes disponíveis"""
        try:
            if not self.login():
                return None
            
            url = f"{self.base_url}/edge/rest/lookups/sports"
            response = requests.get(url, headers=self._get_headers(include_auth=True))
            
            if response.status_code == 200:
                data = response.json()
                return data.get('sports', [])
            else:
                logger.error(f"Erro ao buscar esportes: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar esportes Matchbook: {str(e)}")
            return None
    
    def get_events(self, sport_ids: Optional[List[int]] = None, 
                   after: Optional[str] = None,
                   before: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Busca eventos disponíveis
        
        Args:
            sport_ids: Lista de IDs de esportes (ex: [1] para futebol)
            after: Data início no formato ISO (ex: '2024-12-29T00:00:00Z')
            before: Data fim no formato ISO
        """
        try:
            if not self.login():
                return None
            
            url = f"{self.base_url}/edge/rest/events"
            params = {}
            
            if sport_ids:
                params['sport-ids'] = ','.join(map(str, sport_ids))
            if after:
                params['after'] = after
            if before:
                params['before'] = before
            
            response = requests.get(url, headers=self._get_headers(include_auth=True), params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('events', [])
            else:
                logger.error(f"Erro ao buscar eventos: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar eventos Matchbook: {str(e)}")
            return None
    
    def get_markets(self, event_id: int) -> Optional[List[Dict]]:
        """Busca mercados de um evento específico"""
        try:
            if not self.login():
                return None
            
            url = f"{self.base_url}/edge/rest/events/{event_id}/markets"
            response = requests.get(url, headers=self._get_headers(include_auth=True))
            
            if response.status_code == 200:
                data = response.json()
                return data.get('markets', [])
            else:
                logger.error(f"Erro ao buscar mercados: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar mercados Matchbook: {str(e)}")
            return None
    
    def get_prices(self, event_id: int, market_id: int, runner_id: int) -> Optional[Dict]:
        """Busca preços/odds de um runner específico"""
        try:
            if not self.login():
                return None
            
            url = f"{self.base_url}/edge/rest/events/{event_id}/markets/{market_id}/runners/{runner_id}/prices"
            response = requests.get(url, headers=self._get_headers(include_auth=True))
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao buscar preços: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar preços Matchbook: {str(e)}")
            return None