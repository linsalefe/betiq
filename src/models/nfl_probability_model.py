import numpy as np
from typing import Dict, Tuple
from scipy.stats import norm

class NFLProbabilityModel:
    """Calcula probabilidades para mercados da NFL"""
    
    def __init__(self):
        self.home_advantage = 2.5  # NFL home field advantage ~2.5 pontos
    
    def calculate_over_under(self, home_avg: float, away_avg: float, line: float) -> Dict:
        """
        Calcula probabilidade de Over/Under total de pontos
        
        Args:
            home_avg: Média de pontos do time da casa
            away_avg: Média de pontos do time visitante
            line: Linha do total (ex: 48.5)
        """
        home_expected = home_avg + self.home_advantage
        away_expected = away_avg
        
        total_expected = home_expected + away_expected
        
        # NFL usa distribuição normal (não Poisson como futebol)
        # Desvio padrão típico: ~14 pontos
        std_dev = 14.0
        
        # Probabilidade de over
        prob_over = 1 - norm.cdf(line, loc=total_expected, scale=std_dev)
        prob_under = norm.cdf(line, loc=total_expected, scale=std_dev)
        
        return {
            'prob_over': round(prob_over, 4),
            'prob_under': round(prob_under, 4),
            'expected_points': round(total_expected, 2)
        }
    
    def calculate_spread(self, home_avg: float, away_avg: float, 
                        home_def: float, away_def: float, line: float) -> Dict:
        """
        Calcula probabilidade de cobrir o spread
        
        Args:
            home_avg: Média de pontos marcados (casa)
            away_avg: Média de pontos marcados (visitante)
            home_def: Média de pontos sofridos (casa)
            away_def: Média de pontos sofridos (visitante)
            line: Spread (ex: -3.5 para favorito)
        """
        # Calcula expectativa de pontos usando ataque vs defesa
        home_expected = (home_avg + away_def) / 2 + self.home_advantage
        away_expected = (away_avg + home_def) / 2
        
        expected_diff = home_expected - away_expected
        
        # Desvio padrão para margem de vitória
        std_dev = 13.5
        
        # Probabilidade do favorito cobrir o spread
        if line < 0:  # Home é favorito
            prob_home_cover = 1 - norm.cdf(-line, loc=expected_diff, scale=std_dev)
        else:  # Away é favorito
            prob_home_cover = norm.cdf(line, loc=expected_diff, scale=std_dev)
        
        return {
            'prob_home_cover': round(prob_home_cover, 4),
            'prob_away_cover': round(1 - prob_home_cover, 4),
            'expected_diff': round(expected_diff, 2),
            'line': line
        }
    
    def calculate_moneyline(self, home_avg: float, away_avg: float,
                           home_def: float, away_def: float) -> Dict:
        """
        Calcula probabilidade de vitória (moneyline)
        """
        home_expected = (home_avg + away_def) / 2 + self.home_advantage
        away_expected = (away_avg + home_def) / 2
        
        expected_diff = home_expected - away_expected
        
        # Probabilidade de vitória usando distribuição normal
        std_dev = 13.5
        prob_home_win = 1 - norm.cdf(0, loc=expected_diff, scale=std_dev)
        
        return {
            'prob_home_win': round(prob_home_win, 4),
            'prob_away_win': round(1 - prob_home_win, 4),
            'expected_diff': round(expected_diff, 2)
        }
    
    def calculate_ev(self, model_probability: float, market_odds: float) -> float:
        """Calcula Expected Value (EV)"""
        ev = (model_probability * market_odds) - 1
        ev_percentage = ev * 100
        
        return round(ev_percentage, 2)
    
    def validate_opportunity(self, model_prob: float, odds: float, min_ev: float) -> Tuple[bool, float]:
        """Valida se oportunidade tem EV positivo suficiente"""
        ev = self.calculate_ev(model_prob, odds)
        
        if ev >= min_ev and model_prob > (1 / odds):
            return True, ev
        
        return False, ev

