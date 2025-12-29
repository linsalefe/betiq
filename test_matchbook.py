import os
from dotenv import load_dotenv
from src.services.matchbook_service import MatchbookService

# Carrega variáveis de ambiente
load_dotenv()

def test_matchbook():
    """Testa integração com Matchbook"""
    
    print("=" * 60)
    print("TESTE MATCHBOOK API")
    print("=" * 60)
    
    # Inicializa o serviço
    mb = MatchbookService()
    
    # Teste 1: Login
    print("\n[1] Testando LOGIN...")
    if mb.login():
        print("✅ Login realizado com sucesso!")
        print(f"   Session Token: {mb.session_token[:20]}...")
    else:
        print("❌ Erro no login")
        return
    
    # Teste 2: Buscar esportes
    print("\n[2] Buscando ESPORTES disponíveis...")
    sports = mb.get_sports()
    if sports:
        print(f"✅ {len(sports)} esportes encontrados:")
        for sport in sports[:5]:  # Mostra os 5 primeiros
            print(f"   - ID: {sport.get('id')} | Nome: {sport.get('name')}")
    else:
        print("❌ Erro ao buscar esportes")
        return
    
    # Teste 3: Buscar eventos de futebol (ID geralmente é 1)
    print("\n[3] Buscando EVENTOS de futebol...")
    events = mb.get_events(sport_ids=[1])
    if events:
        print(f"✅ {len(events)} eventos encontrados:")
        for event in events[:3]:  # Mostra os 3 primeiros
            print(f"   - ID: {event.get('id')} | {event.get('name')}")
            print(f"     Data: {event.get('start')}")
    else:
        print("⚠️  Nenhum evento encontrado (pode não ter jogos agendados)")
    
    # Teste 4: Se encontrou eventos, busca mercados do primeiro
    if events and len(events) > 0:
        first_event = events[0]
        event_id = first_event.get('id')
        
        print(f"\n[4] Buscando MERCADOS do evento: {first_event.get('name')}")
        markets = mb.get_markets(event_id)
        if markets:
            print(f"✅ {len(markets)} mercados encontrados:")
            for market in markets[:5]:  # Mostra os 5 primeiros
                print(f"   - ID: {market.get('id')} | Tipo: {market.get('type')}")
                print(f"     Nome: {market.get('name')}")
        else:
            print("⚠️  Nenhum mercado encontrado")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    test_matchbook()