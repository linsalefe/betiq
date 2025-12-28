import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
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
    def get_team_stats_by_venue(self, team_id: int, season: int = 2025) -> Optional[Dict]:
        """
        Busca estatísticas do time separadas por CASA e FORA
        Retorna dict com stats de casa e fora
        Cache: 24 horas
        """
        cache_key = f"team_venue_stats:{team_id}:season_{season}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print(f"📦 Cache: stats do time {team_id}")
            return cached
        
        try:
            # Busca jogos em CASA
            home_matches = self._get_team_matches(team_id, season, venue='HOME', status='FINISHED')
            # Busca jogos FORA
            away_matches = self._get_team_matches(team_id, season, venue='AWAY', status='FINISHED')
            
            if not home_matches and not away_matches:
                return None
            
            # Calcula médias
            home_stats = self._calculate_venue_stats(home_matches, team_id, is_home=True)
            away_stats = self._calculate_venue_stats(away_matches, team_id, is_home=False)
            
            result = {
                'team_id': team_id,
                'season': season,
                'home': home_stats,
                'away': away_stats
            }
            
            # Salva no cache (24 horas)
            self.cache.set(cache_key, result, expire_seconds=86400)
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao buscar stats do time {team_id}: {e}")
            return None
    
    def _get_team_matches(self, team_id: int, season: int, venue: str, status: str) -> List[Dict]:
        """Busca jogos do time filtrados por venue (HOME/AWAY) e status"""
        try:
            url = f"{self.base_url}/teams/{team_id}/matches"
            params = {
                'season': season,
                'venue': venue,
                'status': status
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json().get('matches', [])
        except Exception as e:
            print(f"❌ Erro ao buscar jogos: {e}")
            return []
    
    def _calculate_venue_stats(self, matches: List[Dict], team_id: int, is_home: bool) -> Dict:
        """Calcula estatísticas para casa ou fora"""
        goals_scored = []
        goals_conceded = []
        
        for match in matches:
            score = match.get('score', {}).get('fullTime', {})
            if not score:
                continue
            
            if is_home:
                # Time jogando em casa
                scored = score.get('home', 0)
                conceded = score.get('away', 0)
            else:
                # Time jogando fora
                scored = score.get('away', 0)
                conceded = score.get('home', 0)
            
            goals_scored.append(scored)
            goals_conceded.append(conceded)
        
        games = len(goals_scored)
        
        return {
            'games': games,
            'goals_scored': sum(goals_scored),
            'goals_conceded': sum(goals_conceded),
            'avg_scored': round(sum(goals_scored) / games, 2) if games > 0 else 0.0,
            'avg_conceded': round(sum(goals_conceded) / games, 2) if games > 0 else 0.0
        }
    
    @retry_on_rate_limit(max_retries=3)
    def get_team_id_by_name(self, team_name: str, competition_code: str = 'PL') -> Optional[int]:
        """
        Busca ID do time pelo nome na competição
        Cache: 7 dias (nomes não mudam)
        """
        cache_key = f"team_id:{competition_code}:{team_name}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.base_url}/competitions/{competition_code}/teams"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            teams = response.json().get('teams', [])
            
            # Busca por nome exato ou similar
            for team in teams:
                if team['name'] == team_name or team.get('shortName') == team_name:
                    team_id = team['id']
                    # Cache por 7 dias
                    self.cache.set(cache_key, team_id, expire_seconds=604800)
                    return team_id
            
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar ID do time {team_name}: {e}")
            return None
    
    # Métodos originais mantidos...
    @retry_on_rate_limit(max_retries=3)
    def get_today_matches(self) -> List[Dict]:
        """Busca jogos de hoje (cache: 6 horas)"""
        cache_key = f"matches:today:{datetime.now().strftime('%Y-%m-%d')}"
        
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
