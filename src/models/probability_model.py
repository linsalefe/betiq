import numpy as np
from typing import Dict, Tuple
from scipy.stats import poisson

class ProbabilityModel:
    """Calcula probabilidades para diferentes mercados usando Poisson"""
    
    def __init__(self):
        self.home_advantage = 1.0
    
    def calculate_over_under(self, home_avg: float, away_avg: float, line: float) -> Dict:
        """Calcula probabilidade de Over/Under X.5 gols"""
        home_expected = home_avg * self.home_advantage
        away_expected = away_avg
        
        total_expected = home_expected + away_expected
        
        # Probabilidade de over usando Poisson
        prob_under = sum([poisson.pmf(i, total_expected) for i in range(int(line) + 1)])
        prob_over = 1 - prob_under
        
        return {
            'prob_over': round(prob_over, 4),
            'prob_under': round(prob_under, 4),
            'expected_goals': round(total_expected, 2)
        }
    
    def calculate_btts_from_lambdas(self, home_lambda: float, away_lambda: float) -> float:
        """
        Calcula probabilidade de BTTS usando lambdas diretamente
        
        Args:
            home_lambda: Expectativa de gols do time da casa
            away_lambda: Expectativa de gols do time visitante
        
        Returns:
            Probabilidade de ambos marcarem
        """
        from scipy.stats import poisson
        
        # P(casa marcar) = 1 - P(casa fazer 0 gols)
        home_score_prob = 1 - poisson.pmf(0, home_lambda)
        
        # P(visitante marcar) = 1 - P(visitante fazer 0 gols)
        away_score_prob = 1 - poisson.pmf(0, away_lambda)
        
        # P(ambos marcarem) = P(casa marcar) * P(visitante marcar)
        btts_prob = home_score_prob * away_score_prob
        
        return round(btts_prob, 4)
    
    def calculate_ev(self, model_probability: float, market_odds: float) -> float:
        """Calcula Expected Value (EV)"""
        implied_prob = 1 / market_odds
        ev = (model_probability * market_odds) - 1
        ev_percentage = ev * 100
        
        return round(ev_percentage, 2)
    
    def validate_opportunity(self, model_prob: float, odds: float, min_ev: float) -> Tuple[bool, float]:
        """Valida se oportunidade tem EV positivo suficiente"""
        ev = self.calculate_ev(model_prob, odds)
        
        if ev >= min_ev and model_prob > (1 / odds):
            return True, ev
        
        return False, ev
    def calculate_handicap(self, home_avg: float, away_avg: float, line: float) -> Dict:
        """
        Calcula probabilidade de handicap/spread
        line: handicap (ex: -1.5 para home, +1.5 para away)
        """
        # Estima diferença esperada de gols
        expected_diff = home_avg - away_avg
        
        # Probabilidade do home cobrir o handicap
        # Se line = -1.5, home precisa ganhar por 2+ gols
        # Se expected_diff > line, favorece home
        
        # Modelo simplificado baseado em distribuição normal
        # Em produção, usar simulação de Monte Carlo
        margin = expected_diff - line
        
        # Converte margem em probabilidade (aproximação)
        if margin > 1.5:
            prob_home = 0.75
        elif margin > 0.5:
            prob_home = 0.65
        elif margin > -0.5:
            prob_home = 0.55
        elif margin > -1.5:
            prob_home = 0.45
        else:
            prob_home = 0.35
        
        return {
            'prob_home_cover': prob_home,
            'prob_away_cover': 1 - prob_home,
            'expected_diff': expected_diff,
            'line': line
        }