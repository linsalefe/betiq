from src.services.football_api import FootballAPI
from dotenv import load_dotenv

load_dotenv()

def test_api():
    print("\n" + "="*60)
    print("🧪 TESTANDO FOOTBALL-DATA.ORG API")
    print("="*60)
    
    client = FootballAPI()
    
    # Testa buscar jogos de hoje
    print("\n1️⃣ Buscando jogos de hoje...")
    matches = client.get_today_matches()
    
    if matches:
        print(f"✅ {len(matches)} jogos encontrados!\n")
        
        # Mostra primeiros 5
        for i, match in enumerate(matches[:5], 1):
            print(f"{i}. {match['home_team']} x {match['away_team']}")
            print(f"   Competição: {match['competition']}")
            print(f"   Data: {match['date']}")
            print(f"   Status: {match['status']}\n")
    else:
        print("⚠️  Nenhum jogo encontrado hoje.")
        print("   (Normal se não houver jogos agendados)")
    
    print("="*60)
    print("✅ TESTE CONCLUÍDO")
    print("="*60)

if __name__ == "__main__":
    test_api()