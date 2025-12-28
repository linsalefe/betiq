from typing import Dict, Tuple, List
from datetime import datetime, timedelta

class RiskManager:
    """Gerencia riscos e limites de exposição"""
    
    def __init__(self, bankroll: float, phase: int):
        self.bankroll = bankroll
        self.phase = phase
        self.daily_stakes = []
        self.current_sequence = {'wins': 0, 'losses': 0, 'last_result': None}
    
    def check_daily_limit(self, new_stake: float) -> Tuple[bool, str]:
        """Verifica se pode apostar mais hoje"""
        today = datetime.now().date()
        
        # Remove stakes de dias anteriores
        self.daily_stakes = [
            s for s in self.daily_stakes 
            if datetime.fromisoformat(s['date']).date() == today
        ]
        
        # Calcula exposição de hoje
        today_total = sum(s['stake'] for s in self.daily_stakes)
        
        # Define limite por fase
        daily_limits = {
            1: 0.50,  # 50% da banca
            2: 0.40,  # 40%
            3: 0.25,  # 25%
            4: 0.15,  # 15%
            'consolidation': 0.10  # 10%
        }
        
        phase_key = self.phase if self.phase != 'consolidation' else 'consolidation'
        limit_pct = daily_limits.get(phase_key, 0.50)
        max_daily = self.bankroll * limit_pct
        
        if (today_total + new_stake) > max_daily:
            return False, f"Limite diário atingido (R$ {today_total:.2f} / R$ {max_daily:.2f})"
        
        return True, ""
    
    def check_max_simultaneous(self, pending_count: int) -> Tuple[bool, str]:
        """Verifica número máximo de apostas simultâneas"""
        limits = {
            1: 5,
            2: 4,
            3: 3,
            4: 2,
            'consolidation': 2
        }
        
        phase_key = self.phase if self.phase != 'consolidation' else 'consolidation'
        max_simultaneous = limits.get(phase_key, 5)
        
        if pending_count >= max_simultaneous:
            return False, f"Máximo de apostas simultâneas atingido ({pending_count}/{max_simultaneous})"
        
        return True, ""
    
    def update_sequence(self, result: str):
        """Atualiza sequência de vitórias/derrotas"""
        if result == 'won':
            if self.current_sequence['last_result'] == 'won':
                self.current_sequence['wins'] += 1
            else:
                self.current_sequence['wins'] = 1
                self.current_sequence['losses'] = 0
        elif result == 'lost':
            if self.current_sequence['last_result'] == 'lost':
                self.current_sequence['losses'] += 1
            else:
                self.current_sequence['losses'] = 1
                self.current_sequence['wins'] = 0
        
        self.current_sequence['last_result'] = result
    
    def check_losing_sequence(self) -> Tuple[bool, str]:
        """Verifica sequência de derrotas"""
        max_losses = {
            1: 4,  # Para na 4ª derrota seguida
            2: 3,
            3: 3,
            4: 2,
            'consolidation': 2
        }
        
        phase_key = self.phase if self.phase != 'consolidation' else 'consolidation'
        limit = max_losses.get(phase_key, 4)
        
        if self.current_sequence['losses'] >= limit:
            return False, f"⚠️ {self.current_sequence['losses']} derrotas seguidas. Pause até amanhã."
        
        return True, ""
    
    def get_stake_adjustment(self) -> float:
        """Ajusta stake baseado em sequência"""
        # Reduz stake após 2+ derrotas
        if self.current_sequence['losses'] >= 2:
            return 0.5  # 50% do stake normal
        
        # Mantém stake normal
        return 1.0
    
    def add_stake(self, stake: float):
        """Registra stake do dia"""
        self.daily_stakes.append({
            'stake': stake,
            'date': datetime.now().isoformat()
        })
    
    def get_risk_summary(self) -> Dict:
        """Retorna resumo de risco"""
        today = datetime.now().date()
        today_stakes = [
            s for s in self.daily_stakes 
            if datetime.fromisoformat(s['date']).date() == today
        ]
        
        today_total = sum(s['stake'] for s in today_stakes)
        
        return {
            'daily_exposure': round(today_total, 2),
            'daily_exposure_pct': round((today_total / self.bankroll) * 100, 2),
            'bets_today': len(today_stakes),
            'current_wins': self.current_sequence['wins'],
            'current_losses': self.current_sequence['losses'],
            'stake_adjustment': self.get_stake_adjustment()
        }