import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.llm_service import LLMService
from src.agents.betting_agent import BettingAgent
from dotenv import load_dotenv

load_dotenv()

def test_llm():
    print("\n" + "="*60)
    print("🧪 TESTANDO LLM SERVICE")
    print("="*60)
    
    llm = LLMService()
    agent = BettingAgent(current_bankroll=100)
    
    # Busca oportunidades para dar contexto
    print("\n🔍 Buscando oportunidades...")
    opportunities = agent.analyze_today_opportunities()
    multiples = agent.detect_multiples(opportunities)
    stats = agent.get_statistics()
    
    # Monta contexto
    context = {
        'bankroll': 100,
        'phase': 1,
        'opportunities': opportunities[:3],
        'multiples': multiples[:2],
        'stats': stats
    }
    
    # Testa perguntas
    questions = [
        "Quais os melhores jogos de hoje?",
        "Vale a pena fazer a múltipla?",
        "O que é EV?",
    ]
    
    for question in questions:
        print(f"\n👤 User: {question}")
        response = llm.chat(question, context=context)
        print(f"🤖 Bot: {response}")
        print("-" * 60)
    
    print("\n✅ TESTE CONCLUÍDO\n")

if __name__ == "__main__":
    test_llm()