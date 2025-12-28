from config.config import Config
from typing import Dict, Tuple

class BankrollManager:
    """Gerencia banca, fases e cálculo de stakes"""
    
    def __init__(self, current_bankroll: float):
        self.bankroll = current_bankroll
        self.phase = self._determine_phase()
        
    def _determine_phase(self) -> str:
        """Determina em qual fase o usuário está"""
        if self.bankroll >= Config.CONSOLIDATION_THRESHOLD:
            return 'consolidation'
        elif self.bankroll >= Config.PHASE_TARGETS[3]:
            return 4
        elif self.bankroll >= Config.PHASE_TARGETS[2]:
            return 3
        elif self.bankroll >= Config.PHASE_TARGETS[1]:
            return 2
        else:
            return 1
    
    def get_phase_info(self) -> Dict:
        """Retorna informações da fase atual"""
        if self.phase == 'consolidation':
            return {
                'phase': 'Consolidação',
                'bankroll': self.bankroll,
                'target': None,
                'progress': 100,
                'min_ev': Config.MIN_EV['consolidation'],
                'max_stake_pct': Config.MAX_STAKE['consolidation']
            }
        
        target = Config.PHASE_TARGETS[self.phase]
        progress = (self.bankroll / target) * 100
        
        return {
            'phase': self.phase,
            'bankroll': self.bankroll,
            'target': target,
            'progress': round(progress, 2),
            'remaining': target - self.bankroll,
            'min_ev': Config.MIN_EV[self.phase],
            'max_stake_pct': Config.MAX_STAKE[self.phase]
        }
    
    def calculate_stake(self, probability: float, odds: float, ev: float) -> float:
        """Calcula stake baseado na fase e Kelly fracionado"""
        phase_info = self.get_phase_info()
        max_stake_pct = phase_info['max_stake_pct']
        
        # Kelly fracionado conservador
        kelly_fraction = 0.25 if self.phase == 'consolidation' else 0.5
        edge = (probability * odds) - 1
        
        if edge <= 0:
            return 0
        
        kelly_stake_pct = (edge / (odds - 1)) * kelly_fraction * 100
        
        # Limita ao máximo da fase
        stake_pct = min(kelly_stake_pct, max_stake_pct)
        
        return round((stake_pct / 100) * self.bankroll, 2)
    
    def check_phase_completion(self) -> Tuple[bool, float]:
        """Verifica se atingiu meta da fase e retorna valor pra sacar"""
        if self.phase == 'consolidation':
            return False, 0
        
        target = Config.PHASE_TARGETS[self.phase]
        
        if self.bankroll >= target:
            withdraw_amount = self.bankroll * 0.5
            return True, round(withdraw_amount, 2)
        
        return False, 0
    
    def update_bankroll(self, new_bankroll: float):
        """Atualiza banca e recalcula fase"""
        self.bankroll = new_bankroll
        self.phase = self._determine_phase()