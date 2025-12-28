import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config.config import Config
from src.cache.redis_client import RedisCache
from src.utils.api_retry import retry_on_rate_limit

class FootballAPI:
    """Serviço para buscar dados de jogos com cache Redis"""
    
    def __init__(self):
        self.api_key = Config.FOOTBALL_API_KEY
        self.base_url = Config.FOOTBALL_API_BASE_URL
        self.headers = {'X-Auth-Token': self.api_key}
        self.cache = RedisCache()
    
    @retry_on_rate_limit(max_retries=3)
    def get_today_matches(self) -> List[Dict]:
        """Busca jogos de hoje (cache: 6 horas)"""
        cache_key = f"matches:today:{datetime.now().strftime('%Y-%m-%d')}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print("📦 Usando cache (jogos de hoje)")
            return cached
        
        if not self.api_key or self.api_key == 'your_api_key_here':
            return []
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/matches"
        params = {'dateFrom': today, 'dateTo': today}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        matches = response.json().get('matches', [])
        formatted = self._format_matches(matches)
        
        # Salva no cache (6 horas)
        self.cache.set(cache_key, formatted, expire_seconds=21600)
        
        return formatted
    
    @retry_on_rate_limit(max_retries=3)
    def get_matches_next_days(self, days: int = 7) -> List[Dict]:
        """Busca jogos dos próximos N dias (cache: 6 horas)"""
        cache_key = f"matches:next_{days}days:{datetime.now().strftime('%Y-%m-%d')}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print(f"📦 Usando cache (próximos {days} dias)")
            return cached
        
        if not self.api_key or self.api_key == 'your_api_key_here':
            return []
        
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/matches"
        params = {'dateFrom': date_from, 'dateTo': date_to}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        matches = response.json().get('matches', [])
        formatted = self._format_matches(matches)
        
        # Salva no cache (6 horas)
        self.cache.set(cache_key, formatted, expire_seconds=21600)
        
        return formatted
    
    def _format_matches(self, matches: List[Dict]) -> List[Dict]:
        """Formata dados dos jogos"""
        formatted = []
        
        for match in matches:
            formatted.append({
                'match_id': match['id'],
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'competition': match['competition']['name'],
                'date': match['utcDate'],
                'status': match['status']
            })
        
        return formatted
    
    @retry_on_rate_limit(max_retries=3)
    def get_team_stats(self, team_id: int, last_n_games: int = 5) -> Dict:
        """Busca estatísticas recentes do time (cache: 24 horas)"""
        cache_key = f"team_stats:{team_id}:last_{last_n_games}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print(f"📦 Usando cache (stats time {team_id})")
            return cached
        
        url = f"{self.base_url}/teams/{team_id}/matches"
        params = {'limit': last_n_games}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        matches = response.json().get('matches', [])
        stats = self._calculate_team_stats(matches, team_id)
        
        # Salva no cache (24 horas)
        self.cache.set(cache_key, stats, expire_seconds=86400)
        
        return stats
    
    def _calculate_team_stats(self, matches: List[Dict], team_id: int) -> Dict:
        """Calcula médias de gols"""
        scored = []
        conceded = []
        
        for match in matches:
            if match['status'] != 'FINISHED':
                continue
            
            is_home = match['homeTeam']['id'] == team_id
            
            if is_home:
                scored.append(match['score']['fullTime']['home'])
                conceded.append(match['score']['fullTime']['away'])
            else:
                scored.append(match['score']['fullTime']['away'])
                conceded.append(match['score']['fullTime']['home'])
        
        return {
            'avg_scored': round(sum(scored) / len(scored), 2) if scored else 0,
            'avg_conceded': round(sum(conceded) / len(conceded), 2) if conceded else 0,
            'games_analyzed': len(scored)
        }