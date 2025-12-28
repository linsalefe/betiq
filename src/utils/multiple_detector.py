from typing import List, Dict
from itertools import combinations

class MultipleDetector:
    """Detecta e monta múltiplas estratégicas"""
    
    @staticmethod
    def can_combine(opp1: Dict, opp2: Dict) -> bool:
        """Verifica se duas apostas podem ser combinadas"""
        # Não combina mesmo jogo
        if opp1['match'] == opp2['match']:
            return False
        
        # Não combina mesma competição no mesmo horário (correlação)
        if opp1['competition'] == opp2['competition']:
            return False
        
        return True
    
    @staticmethod
    def calculate_combined_probability(opps: List[Dict]) -> float:
        """Calcula probabilidade combinada"""
        prob = 1.0
        for opp in opps:
            prob *= opp['probability']
        return prob
    
    @staticmethod
    def calculate_combined_odds(opps: List[Dict]) -> float:
        """Calcula odd combinada"""
        odds = 1.0
        for opp in opps:
            odds *= opp['odds']
        return round(odds, 2)
    
    @staticmethod
    def detect_multiples(opportunities: List[Dict], min_combined_prob: float = 0.30, 
                        max_legs: int = 3) -> List[Dict]:
        """Detecta múltiplas estratégicas"""
        multiples = []
        
        # Testa combinações de 2 e 3 pernas
        for n_legs in range(2, max_legs + 1):
            for combo in combinations(opportunities, n_legs):
                # Verifica se todas podem ser combinadas
                valid = True
                for i in range(len(combo)):
                    for j in range(i + 1, len(combo)):
                        if not MultipleDetector.can_combine(combo[i], combo[j]):
                            valid = False
                            break
                    if not valid:
                        break
                
                if not valid:
                    continue
                
                # Calcula probabilidade e odds combinadas
                combined_prob = MultipleDetector.calculate_combined_probability(list(combo))
                combined_odds = MultipleDetector.calculate_combined_odds(list(combo))
                
                # Só aceita se probabilidade combinada >= mínimo
                if combined_prob < min_combined_prob:
                    continue
                
                # Calcula EV da múltipla
                combined_ev = ((combined_prob * combined_odds) - 1) * 100
                
                # Só aceita múltiplas com EV positivo
                if combined_ev <= 0:
                    continue
                
                multiples.append({
                    'legs': list(combo),
                    'n_legs': n_legs,
                    'combined_odds': combined_odds,
                    'combined_probability': round(combined_prob, 4),
                    'combined_ev': round(combined_ev, 2)
                })
        
        # Ordena por EV
        multiples.sort(key=lambda x: x['combined_ev'], reverse=True)
        
        return multiples
    
    @staticmethod
    def format_multiple(multiple: Dict, stake: float) -> Dict:
        """Formata múltipla para exibição"""
        potential_return = stake * multiple['combined_odds']
        
        return {
            'type': 'multiple',
            'n_legs': multiple['n_legs'],
            'legs': [
                {
                    'match': leg['match'],
                    'market': leg['market'],
                    'odds': leg['odds']
                }
                for leg in multiple['legs']
            ],
            'combined_odds': multiple['combined_odds'],
            'probability': multiple['combined_probability'],
            'ev': multiple['combined_ev'],
            'stake': round(stake, 2),
            'potential_return': round(potential_return, 2),
            'potential_profit': round(potential_return - stake, 2)
        }