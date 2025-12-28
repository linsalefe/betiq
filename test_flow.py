from src.agents.betting_agent import BettingAgent
from dotenv import load_dotenv

def test_complete_flow():
    load_dotenv()
    
    print("\n" + "=" * 60)
    print("🧪 TESTANDO FLUXO COMPLETO DO AGENTE")
    print("=" * 60)
    
    # Inicia agente
    agent = BettingAgent(current_bankroll=100)
    
    # 1. Busca oportunidades
    print("\n1️⃣ Buscando oportunidades...")
    opportunities = agent.analyze_today_opportunities()
    print(f"✅ {len(opportunities)} oportunidades encontradas\n")
    
    # 2. Registra primeira aposta
    if opportunities:
        bet = opportunities[0]
        print("2️⃣ Registrando aposta:")
        print(f"   {bet['match']} - {bet['market']}")
        print(f"   Stake: R$ {bet['stake']:.2f} | Odd: {bet['odds']}")
        
        bet_id = agent.register_bet(bet)
        print(f"✅ Aposta registrada: {bet_id}\n")
        
        # 3. Simula vitória
        print("3️⃣ Atualizando resultado: VITÓRIA")
        agent.update_bet_result(bet_id, 'won')
        print("✅ Resultado atualizado\n")
        
        # 4. Mostra estatísticas
        print("4️⃣ Estatísticas atualizadas:")
        stats = agent.get_statistics()
        print(f"   Total apostas: {stats['total_bets']}")
        print(f"   Vitórias: {stats['won']}")
        print(f"   Win rate: {stats['win_rate']:.1f}%")
        print(f"   ROI: {stats['roi']:.2f}%")
        print(f"   Lucro: R$ {stats['total_profit']:.2f}\n")
        
        # 5. Testa sequência de derrotas
        print("5️⃣ Testando controle de risco (3 derrotas)...")
        for i in range(3):
            bet_test = {
                'match': f'Teste {i+1}',
                'competition': 'Teste',
                'market': 'Over 2.5',
                'odds': 2.0,
                'stake': 10,
                'probability': 0.6,
                'ev': 10,
                'phase': 1
            }
            bid = agent.register_bet(bet_test)
            agent.update_bet_result(bid, 'lost')
        
        risk = agent.risk_manager.get_risk_summary()
        print(f"✅ Sequência de derrotas: {risk['current_losses']}")
        print(f"✅ Ajuste de stake: {risk['stake_adjustment']*100:.0f}%\n")
        
        # 6. Estatísticas finais
        print("6️⃣ Estatísticas finais:")
        final_stats = agent.get_statistics()
        print(f"   Total: {final_stats['total_bets']} apostas")
        print(f"   Vitórias: {final_stats['won']} | Derrotas: {final_stats['lost']}")
        print(f"   Win rate: {final_stats['win_rate']:.1f}%")
        print(f"   Total apostado: R$ {final_stats['total_staked']:.2f}")
        print(f"   Lucro/Prejuízo: R$ {final_stats['total_profit']:.2f}")
        print(f"   ROI: {final_stats['roi']:.2f}%\n")
    
    print("=" * 60)
    print("✅ TESTE COMPLETO FINALIZADO")
    print("=" * 60)

if __name__ == "__main__":
    test_complete_flow()