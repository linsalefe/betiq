import numpy as np
from typing import Dict, Tuple
from scipy.stats import norm

class TennisProbabilityModel:
    """Calcula probabilidades para mercados de Tênis"""
    
    def __init__(self):
        # Tênis não tem home advantage significativo (apenas altitude/superfície)
        self.surface_advantage = {
            'clay': 0.05,    # 5% boost para especialistas
            'grass': 0.03,
            'hard': 0.02
        }
    
    def calculate_match_winner(self, player1_win_rate: float, player2_win_rate: float,
                               surface: str = 'hard', head_to_head: Dict = None) -> Dict:
        """
        Calcula probabilidade de vitória
        
        Args:
            player1_win_rate: Taxa de vitória do jogador 1 (0-100%)
            player2_win_rate: Taxa de vitória do jogador 2 (0-100%)
            surface: Superfície (clay, grass, hard)
            head_to_head: Histórico direto {player1_wins, player2_wins}
        """
        # Normaliza win rates
        p1_base = player1_win_rate / 100
        p2_base = player2_win_rate / 100
        
        # Ajusta pela superfície (se tiver dados históricos por superfície, usar aqui)
        p1_adjusted = p1_base
        p2_adjusted = p2_base
        
        # Ajusta por head-to-head se disponível
        if head_to_head:
            h2h_total = head_to_head.get('player1_wins', 0) + head_to_head.get('player2_wins', 0)
            if h2h_total > 0:
                h2h_factor = head_to_head.get('player1_wins', 0) / h2h_total
                # Dá 20% de peso ao H2H
                p1_adjusted = 0.8 * p1_adjusted + 0.2 * h2h_factor
                p2_adjusted = 0.8 * p2_adjusted + 0.2 * (1 - h2h_factor)
        
        # Normaliza probabilidades
        total = p1_adjusted + p2_adjusted
        prob_p1 = p1_adjusted / total
        prob_p2 = p2_adjusted / total
        
        return {
            'prob_player1_win': round(prob_p1, 4),
            'prob_player2_win': round(prob_p2, 4)
        }
    
    def calculate_total_games(self, player1_win_rate: float, player2_win_rate: float,
                             best_of: int, line: float) -> Dict:
        """
        Calcula probabilidade de Over/Under total de games
        
        Args:
            player1_win_rate: Taxa de vitória jogador 1
            player2_win_rate: Taxa de vitória jogador 2
            best_of: 3 ou 5 sets
            line: Linha do total (ex: 22.5 games)
        """
        # Calcula número esperado de games baseado em equilíbrio
        if abs(player1_win_rate - player2_win_rate) < 10:
            # Partida equilibrada = mais games
            if best_of == 3:
                expected_games = 25  # Tende a 3 sets próximos
            else:
                expected_games = 38  # Tende a 5 sets
        else:
            # Partida desigual = menos games
            if best_of == 3:
                expected_games = 20  # Provável 2-0
            else:
                expected_games = 30  # Provável 3-0 ou 3-1
        
        # Desvio padrão
        std_dev = 5.0 if best_of == 3 else 7.0
        
        # Probabilidades
        prob_over = 1 - norm.cdf(line, loc=expected_games, scale=std_dev)
        prob_under = norm.cdf(line, loc=expected_games, scale=std_dev)
        
        return {
            'prob_over': round(prob_over, 4),
            'prob_under': round(prob_under, 4),
            'expected_games': round(expected_games, 2)
        }
    
    def calculate_set_betting(self, player1_win_rate: float, player2_win_rate: float,
                             best_of: int, exact_score: str) -> float:
        """
        Calcula probabilidade de placar exato
        
        Args:
            exact_score: "2-0", "2-1", "3-0", "3-1", "3-2"
        """
        prob_winner = self.calculate_match_winner(player1_win_rate, player2_win_rate)
        p1_win = prob_winner['prob_player1_win']
        
        # Probabilidades simplificadas por placar
        if best_of == 3:
            probs = {
                '2-0': p1_win * 0.55,
                '2-1': p1_win * 0.45,
                '0-2': (1 - p1_win) * 0.55,
                '1-2': (1 - p1_win) * 0.45
            }
        else:  # best_of == 5
            probs = {
                '3-0': p1_win * 0.35,
                '3-1': p1_win * 0.40,
                '3-2': p1_win * 0.25,
                '0-3': (1 - p1_win) * 0.35,
                '1-3': (1 - p1_win) * 0.40,
                '2-3': (1 - p1_win) * 0.25
            }
        
        return round(probs.get(exact_score, 0), 4)
    
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
