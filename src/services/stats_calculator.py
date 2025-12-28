from typing import List, Dict
from src.services.football_api import FootballAPI

class StatsCalculator:
    """Calcula estatísticas de times baseado em jogos recentes"""
    
    def __init__(self):
        self.football_api = FootballAPI()
    
    def calculate_team_stats_from_matches(self, team_name: str, matches: List[Dict]) -> Dict:
        """Calcula estatísticas de um time baseado em lista de jogos"""
        team_matches = []
        
        for match in matches:
            if match['status'] != 'FINISHED':
                continue
            
            is_home = team_name.lower() in match['home_team'].lower()
            is_away = team_name.lower() in match['away_team'].lower()
            
            if is_home or is_away:
                team_matches.append({
                    'is_home': is_home,
                    'match': match
                })
        
        if not team_matches:
            return {
                'avg_scored': 1.5,  # Default
                'avg_conceded': 1.5,  # Default
                'games_analyzed': 0
            }
        
        # Pega últimos 5 jogos
        recent = team_matches[-5:]
        
        scored = []
        conceded = []
        
        # Note: Precisaríamos dos scores, que o free tier não retorna
        # Por ora, vamos usar valores padrão baseados na liga
        
        return {
            'avg_scored': 1.8,  # Placeholder
            'avg_conceded': 1.2,  # Placeholder  
            'games_analyzed': len(recent)
        }