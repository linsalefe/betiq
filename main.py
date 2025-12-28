from src.agents.betting_agent import BettingAgent
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("=" * 60)
    print("🤖 AGENTE DE VALUE BETTING - INICIANDO")
    print("=" * 60)
    
    # Inicia com banca de R$ 100
    agent = BettingAgent(current_bankroll=100)
    
    # Busca oportunidades
    print("\n🔍 Analisando oportunidades do dia...\n")
    opportunities = agent.analyze_today_opportunities()
    
    if not opportunities:
        print("❌ Nenhuma oportunidade encontrada hoje.")
        return
    
    # Gera relatório completo
    report = agent.get_full_report(opportunities)
    print(report)
    
    print("=" * 60)

if __name__ == "__main__":
    main()