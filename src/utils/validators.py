from typing import Dict, Tuple, List

class OpportunityValidator:
    """Valida oportunidades antes de sugerir"""
    
    @staticmethod
    def validate_odds_range(odds: float, min_odds: float = 1.5, max_odds: float = 3.0) -> Tuple[bool, str]:
        """Valida se odds está em range aceitável"""
        if odds < min_odds:
            return False, f"Odds muito baixa ({odds}). Risco não compensa."
        if odds > max_odds:
            return False, f"Odds muito alta ({odds}). Variância excessiva."
        return True, ""
    
    @staticmethod
    def validate_probability(probability: float, min_prob: float = 0.45) -> Tuple[bool, str]:
        """Valida probabilidade mínima"""
        if probability < min_prob:
            return False, f"Probabilidade muito baixa ({probability*100:.1f}%)"
        return True, ""
    
    @staticmethod
    def validate_ev(ev: float, min_ev: float) -> Tuple[bool, str]:
        """Valida EV mínimo"""
        if ev < min_ev:
            return False, f"EV insuficiente ({ev:.1f}%). Mínimo: {min_ev}%"
        return True, ""
    
    @staticmethod
    def validate_stake(stake: float, bankroll: float, max_stake_pct: float) -> Tuple[bool, str]:
        """Valida stake calculado"""
        stake_pct = (stake / bankroll) * 100
        if stake_pct > max_stake_pct:
            return False, f"Stake excede limite ({stake_pct:.1f}% > {max_stake_pct}%)"
        if stake < 1:
            return False, "Stake muito pequeno (< R$ 1)"
        return True, ""
    
    @staticmethod
    def validate_opportunity(opp: Dict, phase_info: Dict, bankroll: float) -> Tuple[bool, List[str]]:
        """Valida oportunidade completa"""
        errors = []
        
        # Valida odds
        valid, msg = OpportunityValidator.validate_odds_range(opp['odds'])
        if not valid:
            errors.append(msg)
        
        # Valida probabilidade
        valid, msg = OpportunityValidator.validate_probability(opp['probability'])
        if not valid:
            errors.append(msg)
        
        # Valida EV
        valid, msg = OpportunityValidator.validate_ev(opp['ev'], phase_info['min_ev'])
        if not valid:
            errors.append(msg)
        
        # Valida stake
        valid, msg = OpportunityValidator.validate_stake(
            opp['stake'], 
            bankroll, 
            phase_info['max_stake_pct']
        )
        if not valid:
            errors.append(msg)
        
        return len(errors) == 0, errors