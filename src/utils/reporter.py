from typing import Dict, List
from datetime import datetime, timedelta

class Reporter:
    """Gera relatórios e análises"""
    
    @staticmethod
    def generate_daily_report(opportunities: List[Dict], phase_info: Dict, 
                             risk_summary: Dict) -> str:
        """Gera relatório diário"""
        report = f"""
{'='*60}
📊 RELATÓRIO DIÁRIO - {datetime.now().strftime('%d/%m/%Y %H:%M')}
{'='*60}

🎯 FASE ATUAL: {phase_info['phase']}
💰 Banca: R$ {phase_info['bankroll']:.2f}
"""
        
        if phase_info['phase'] != 'Consolidação':
            report += f"""📈 Meta: R$ {phase_info['target']:.2f}
🎲 Progresso: {phase_info['progress']:.1f}%
💵 Faltam: R$ {phase_info['remaining']:.2f}
"""
        
        report += f"""
⚙️ CONTROLES DE RISCO:
- EV mínimo: {phase_info['min_ev']}%
- Stake máximo: {phase_info['max_stake_pct']}%
- Exposição hoje: R$ {risk_summary['daily_exposure']:.2f} ({risk_summary['daily_exposure_pct']:.1f}%)
- Apostas hoje: {risk_summary['bets_today']}
- Sequência: {risk_summary['current_wins']}W / {risk_summary['current_losses']}L
"""
        
        if risk_summary['stake_adjustment'] < 1.0:
            report += f"⚠️ Stakes reduzidos para {risk_summary['stake_adjustment']*100:.0f}% (sequência negativa)\n"
        
        report += f"\n📋 OPORTUNIDADES ENCONTRADAS: {len(opportunities)}\n"
        
        return report
    
    @staticmethod
    def format_opportunity_list(opportunities: List[Dict], max_show: int = 5) -> str:
        """Formata lista de oportunidades"""
        output = ""
        
        for i, opp in enumerate(opportunities[:max_show], 1):
            output += f"""
{i}. {opp['match']}
   Competição: {opp['competition']}
   Mercado: {opp['market']} | Odd: {opp['odds']}
   Probabilidade: {opp['probability']*100:.1f}% | EV: +{opp['ev']:.1f}%
   💰 Stake sugerido: R$ {opp['stake']:.2f}
   🎯 Retorno potencial: R$ {opp['potential_return']:.2f}
"""
        
        if len(opportunities) > max_show:
            output += f"\n... e mais {len(opportunities) - max_show} oportunidades\n"
        
        return output
    
    @staticmethod
    def format_multiple_suggestion(multiple: Dict) -> str:
        """Formata sugestão de múltipla"""
        output = f"""
🎯 MÚLTIPLA RECOMENDADA ({multiple['n_legs']} pernas)
Odd combinada: {multiple['combined_odds']} | Prob: {multiple['probability']*100:.1f}% | EV: +{multiple['ev']:.1f}%

Pernas:
"""
        for i, leg in enumerate(multiple['legs'], 1):
            output += f"  {i}. {leg['match']} - {leg['market']} @ {leg['odds']}\n"
        
        output += f"""
💰 Stake sugerido: R$ {multiple['stake']:.2f}
🎯 Retorno potencial: R$ {multiple['potential_return']:.2f}
💵 Lucro potencial: R$ {multiple['potential_profit']:.2f}
"""
        
        return output
    
    @staticmethod
    def generate_statistics_report(stats: Dict) -> str:
        """Gera relatório de estatísticas"""
        if stats['total_bets'] == 0:
            return "\n📊 ESTATÍSTICAS: Nenhuma aposta registrada ainda.\n"
        
        report = f"""
{'='*60}
📊 ESTATÍSTICAS
{'='*60}

📈 RESUMO GERAL:
- Total de apostas: {stats['total_bets']}
- Vitórias: {stats['won']} ({stats['win_rate']:.1f}%)
- Derrotas: {stats['lost']}
- Anuladas: {stats['void']}

💰 FINANCEIRO:
- Total apostado: R$ {stats['total_staked']:.2f}
- Lucro/Prejuízo: R$ {stats['total_profit']:.2f}
- ROI: {stats['roi']:.2f}%

📊 MÉDIAS:
- Odd média: {stats['avg_odds']:.2f}
- Stake médio: R$ {stats['avg_stake']:.2f}
"""
        
        return report
    
    @staticmethod
    def generate_phase_completion_alert(phase: int, withdraw_amount: float, 
                                       new_bankroll: float) -> str:
        """Gera alerta de conclusão de fase"""
        return f"""
{'='*60}
🎉 FASE {phase} CONCLUÍDA!
{'='*60}

✅ Meta atingida!

🏦 PROTOCOLO DE SAQUE:
- Retire AGORA: R$ {withdraw_amount:.2f} (50% da banca)
- Mantenha operando: R$ {new_bankroll:.2f}

⚠️ IMPORTANTE: 
Execute o saque hoje e confirme para continuar.
Isso protege seus lucros e reduz risco.

Próxima fase inicia com R$ {new_bankroll:.2f}
{'='*60}
"""