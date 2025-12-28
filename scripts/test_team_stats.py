import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.football_api import FootballAPI
from dotenv import load_dotenv

load_dotenv()

def test_team_stats():
    print("\n" + "="*60)
    print("🧪 TESTANDO ESTATÍSTICAS DE TIMES")
    print("="*60)
    
    api = FootballAPI()
    
    # IDs de times conhecidos
    teams = {
        'Manchester City': 65,
        'Liverpool': 64,
        'Real Madrid': 86,
        'Barcelona': 81
    }
    
    for team_name, team_id in teams.items():
        print(f"\n📊 {team_name} (ID: {team_id})")
        stats = api.get_team_stats(team_id, last_n_games=5)
        
        if stats:
            print(f"✅ Últimos {stats['games_analyzed']} jogos:")
            print(f"   Gols marcados (média): {stats['avg_scored']}")
            print(f"   Gols sofridos (média): {stats['avg_conceded']}")
        else:
            print("⚠️  Não foi possível buscar estatísticas")
    
    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO")
    print("="*60)

if __name__ == "__main__":
    test_team_stats()