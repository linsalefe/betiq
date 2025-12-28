from typing import Dict, List
from statistics import mean

class AdvancedStats:
    """Calcula estatísticas avançadas para melhorar probabilidades"""
    
    @staticmethod
    def calculate_form_factor(recent_results: List[str]) -> float:
        """
        Calcula fator de forma baseado em resultados recentes
        recent_results: ['W', 'W', 'L', 'D', 'W'] (últimos 5 jogos)
        """
        if not recent_results:
            return 1.0
        
        points = {'W': 3, 'D': 1, 'L': 0}
        total_points = sum(points.get(r, 0) for r in recent_results)
        max_points = len(recent_results) * 3
        
        # Retorna fator entre 0.8 e 1.2
        form_ratio = total_points / max_points
        return 0.8 + (form_ratio * 0.4)
    
    @staticmethod
    def calculate_home_advantage(is_home: bool) -> float:
        """Calcula vantagem de mando de campo"""
        # Estatisticamente, mandante tem ~15% mais chance
        return 1.15 if is_home else 0.95
    
    @staticmethod
    def adjust_goals_by_form(base_goals: float, form_factor: float, home_advantage: float) -> float:
        """Ajusta média de gols por forma e mando"""
        adjusted = base_goals * form_factor * home_advantage
        return round(adjusted, 2)
    
    @staticmethod
    def calculate_h2h_factor(h2h_results: List[Dict]) -> Dict:
        """
        Calcula fator baseado em confrontos diretos
        h2h_results: [{'home_score': 2, 'away_score': 1}, ...]
        """
        if not h2h_results:
            return {'home_avg': 0, 'away_avg': 0, 'total_avg': 0}
        
        home_goals = [r['home_score'] for r in h2h_results]
        away_goals = [r['away_score'] for r in h2h_results]
        
        return {
            'home_avg': round(mean(home_goals), 2) if home_goals else 0,
            'away_avg': round(mean(away_goals), 2) if away_goals else 0,
            'total_avg': round(mean(home_goals + away_goals), 2)
        }
    
    @staticmethod
    def get_enhanced_stats(team_data: Dict) -> Dict:
        """
        Calcula stats melhoradas para um time
        
        team_data = {
            'base_avg_scored': 1.8,
            'base_avg_conceded': 1.2,
            'recent_form': ['W', 'W', 'L', 'D', 'W'],
            'is_home': True,
            'h2h': [{'home_score': 2, 'away_score': 1}, ...]
        }
        """
        # Fatores
        form_factor = AdvancedStats.calculate_form_factor(
            team_data.get('recent_form', [])
        )
        
        home_advantage = AdvancedStats.calculate_home_advantage(
            team_data.get('is_home', False)
        )
        
        # Ajusta gols
        adjusted_scored = AdvancedStats.adjust_goals_by_form(
            team_data.get('base_avg_scored', 1.5),
            form_factor,
            home_advantage
        )
        
        adjusted_conceded = AdvancedStats.adjust_goals_by_form(
            team_data.get('base_avg_conceded', 1.5),
            1.0,  # Conceded não sofre tanto impacto de forma
            1.0 / home_advantage  # Inverso do advantage
        )
        
        return {
            'avg_scored': adjusted_scored,
            'avg_conceded': adjusted_conceded,
            'form_factor': form_factor,
            'home_advantage': home_advantage
        }