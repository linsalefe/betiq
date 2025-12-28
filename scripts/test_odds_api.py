import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.odds_api import OddsAPI
from dotenv import load_dotenv

load_dotenv()

def test_api():
    print("\n" + "="*60)
    print("🧪 TESTANDO THE ODDS API")
    print("="*60)
    
    client = OddsAPI()
    
    # Testa buscar odds
    print("\n1️⃣ Buscando odds para futebol...")
    
    # Testa diferentes esportes
    sports = ['soccer_epl', 'soccer_spain_la_liga', 'soccer_brazil_campeonato']
    
    total_games = 0
    for sport in sports:
        print(f"\n📊 Sport: {sport}")
        odds = client.get_odds_for_match(sport)
        
        if odds:
            print(f"✅ {len(odds)} jogos encontrados!")
            total_games += len(odds)
            
            # Mostra primeiro jogo
            if odds:
                game = odds[0]
                print(f"\nExemplo: {game['home_team']} x {game['away_team']}")
                print(f"Mercados disponíveis: {list(game['markets'].keys())}")
        else:
            print("⚠️  Nenhum jogo encontrado")
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL: {total_games} jogos com odds")
    print("="*60)

if __name__ == "__main__":
    test_api()