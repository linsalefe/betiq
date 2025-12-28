import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.advanced_stats import AdvancedStats

def test_stats():
    print("\n" + "="*60)
    print("🧪 TESTANDO ESTATÍSTICAS AVANÇADAS")
    print("="*60)
    
    # Teste 1: Forma recente
    print("\n1️⃣ TESTE DE FORMA RECENTE:")
    forms = {
        'Excelente': ['W', 'W', 'W', 'W', 'W'],
        'Boa': ['W', 'W', 'W', 'D', 'L'],
        'Regular': ['W', 'D', 'L', 'D', 'W'],
        'Ruim': ['L', 'L', 'D', 'L', 'W'],
        'Péssima': ['L', 'L', 'L', 'L', 'L']
    }
    
    for label, form in forms.items():
        factor = AdvancedStats.calculate_form_factor(form)
        print(f"  {label:12} {form} → Fator: {factor:.2f}")
    
    # Teste 2: Mando de campo
    print("\n2️⃣ TESTE DE MANDO DE CAMPO:")
    print(f"  Casa: {AdvancedStats.calculate_home_advantage(True):.2f}x")
    print(f"  Fora: {AdvancedStats.calculate_home_advantage(False):.2f}x")
    
    # Teste 3: Stats melhoradas
    print("\n3️⃣ TESTE DE STATS MELHORADAS:")
    
    # Time em boa forma jogando em casa
    home_team = {
        'base_avg_scored': 1.8,
        'base_avg_conceded': 1.2,
        'recent_form': ['W', 'W', 'W', 'D', 'W'],  # Boa forma
        'is_home': True
    }
    
    # Time em má forma jogando fora
    away_team = {
        'base_avg_scored': 1.5,
        'base_avg_conceded': 1.3,
        'recent_form': ['L', 'L', 'D', 'L', 'W'],  # Má forma
        'is_home': False
    }
    
    home_stats = AdvancedStats.get_enhanced_stats(home_team)
    away_stats = AdvancedStats.get_enhanced_stats(away_team)
    
    print("\n  TIME DA CASA (boa forma):")
    print(f"    Base: {home_team['base_avg_scored']} gols/jogo")
    print(f"    Ajustado: {home_stats['avg_scored']} gols/jogo")
    print(f"    Fator forma: {home_stats['form_factor']:.2f}")
    print(f"    Fator casa: {home_stats['home_advantage']:.2f}")
    
    print("\n  TIME VISITANTE (má forma):")
    print(f"    Base: {away_team['base_avg_scored']} gols/jogo")
    print(f"    Ajustado: {away_stats['avg_scored']} gols/jogo")
    print(f"    Fator forma: {away_stats['form_factor']:.2f}")
    print(f"    Fator fora: {away_stats['home_advantage']:.2f}")
    
    # Teste 4: Impacto no Over/Under
    print("\n4️⃣ IMPACTO NO OVER 2.5:")
    total_goals_base = home_team['base_avg_scored'] + away_team['base_avg_scored']
    total_goals_adjusted = home_stats['avg_scored'] + away_stats['avg_scored']
    
    print(f"  Total base: {total_goals_base:.2f} gols")
    print(f"  Total ajustado: {total_goals_adjusted:.2f} gols")
    print(f"  Diferença: {total_goals_adjusted - total_goals_base:+.2f} gols")
    
    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_stats()