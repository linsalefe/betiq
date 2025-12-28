import requests
from datetime import datetime, timedelta
from typing import List, Dict
from src.cache.redis_client import RedisCache
from src.utils.api_retry import retry_on_rate_limit

class NFLAPI:
    """Serviço para buscar dados da NFL via ESPN API"""
    
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        self.cache = RedisCache()
    
    @retry_on_rate_limit(max_retries=3)
    def get_today_games(self) -> List[Dict]:
        """Busca jogos de hoje (cache: 6 horas)"""
        cache_key = f"nfl:games:today:{datetime.now().strftime('%Y-%m-%d')}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print("📦 Usando cache (NFL jogos de hoje)")
            return cached
        
        url = f"{self.base_url}/scoreboard"
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        games = data.get('events', [])
        formatted = self._format_games(games)
        
        # Salva no cache (6 horas)
        self.cache.set(cache_key, formatted, expire_seconds=21600)
        
        return formatted
    
    @retry_on_rate_limit(max_retries=3)
    def get_week_games(self) -> List[Dict]:
        """Busca jogos da semana atual (cache: 6 horas)"""
        cache_key = f"nfl:games:week:{datetime.now().strftime('%Y-W%W')}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print("📦 Usando cache (NFL jogos da semana)")
            return cached
        
        url = f"{self.base_url}/scoreboard"
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        games = data.get('events', [])
        formatted = self._format_games(games)
        
        # Salva no cache (6 horas)
        self.cache.set(cache_key, formatted, expire_seconds=21600)
        
        return formatted
    
    def _format_games(self, games: List[Dict]) -> List[Dict]:
        """Formata dados dos jogos"""
        formatted = []
        
        for game in games:
            try:
                competition = game.get('competitions', [{}])[0]
                home_team = competition.get('competitors', [{}])[0]
                away_team = competition.get('competitors', [{}])[1]
                
                formatted.append({
                    'game_id': game.get('id'),
                    'home_team': home_team.get('team', {}).get('displayName', 'Unknown'),
                    'away_team': away_team.get('team', {}).get('displayName', 'Unknown'),
                    'date': game.get('date'),
                    'status': game.get('status', {}).get('type', {}).get('name', 'scheduled'),
                    'home_score': home_team.get('score', 0),
                    'away_score': away_team.get('score', 0),
                })
            except (KeyError, IndexError) as e:
                print(f"⚠️ Erro ao formatar jogo: {e}")
                continue
        
        return formatted
    
    @retry_on_rate_limit(max_retries=3)
    def get_team_stats(self, team_name: str, last_n_games: int = 5) -> Dict:
        """Busca estatísticas recentes do time (cache: 24 horas)"""
        cache_key = f"nfl:team_stats:{team_name}:last_{last_n_games}"
        
        # Tenta cache
        cached = self.cache.get(cache_key)
        if cached:
            print(f"📦 Usando cache (NFL stats {team_name})")
            return cached
        
        # ESPN API não tem endpoint direto de stats por time
        # Vamos calcular a partir dos jogos da semana
        games = self.get_week_games()
        
        team_games = [g for g in games if team_name in [g['home_team'], g['away_team']]]
        stats = self._calculate_team_stats(team_games[-last_n_games:], team_name)
        
        # Salva no cache (24 horas)
        self.cache.set(cache_key, stats, expire_seconds=86400)
        
        return stats
    
    def _calculate_team_stats(self, games: List[Dict], team_name: str) -> Dict:
        """Calcula médias de pontos marcados/sofridos"""
        scored = []
        conceded = []
        
        for game in games:
            if game['status'] != 'STATUS_FINAL':
                continue
            
            is_home = game['home_team'] == team_name
            
            if is_home:
                scored.append(int(game['home_score']))
                conceded.append(int(game['away_score']))
            else:
                scored.append(int(game['away_score']))
                conceded.append(int(game['home_score']))
        
        return {
            'avg_scored': round(sum(scored) / len(scored), 2) if scored else 0,
            'avg_conceded': round(sum(conceded) / len(conceded), 2) if conceded else 0,
            'games_analyzed': len(scored)
        }
