from src.services.odds_api import OddsAPI
from dotenv import load_dotenv

load_dotenv()

api = OddsAPI()

print("\n🔍 Testando extração de Under...\n")

# Busca odds da Premier League
odds = api.get_odds_for_sport('soccer_epl')

print(f"Total de jogos: {len(odds)}\n")

# Verifica os primeiros 5 jogos
for i, game in enumerate(odds[:5], 1):
    print(f"{i}. {game['home_team']} x {game['away_team']}")
    markets = game['markets']
    
    if 'under_2.5' in markets:
        print(f"   ✅ Under 2.5: {markets['under_2.5']}")
    else:
        print(f"   ❌ Under 2.5: NÃO DISPONÍVEL")
    
    if 'over_2.5' in markets:
        print(f"   ✅ Over 2.5: {markets['over_2.5']}")
    else:
        print(f"   ❌ Over 2.5: NÃO DISPONÍVEL")
    
    print()

print("\n✅ Teste completo!")