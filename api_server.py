from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv

from src.agents.betting_agent import BettingAgent
from src.services.llm_service import LLMService
from src.models.bet_history import BetHistory

load_dotenv()

# Inicializa serviço LLM
llm_service = LLMService()

app = FastAPI(title="Value Betting API")


# =========================
# CORS
# =========================
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Models
# =========================
class OpportunitiesRequest(BaseModel):
    bankroll: float


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class BetRequest(BaseModel):
    match: str
    market: str
    odds: float
    stake: float
    phase: int


# =========================
# Helpers
# =========================
def _needs_context(message: str) -> bool:
    """Detecta se mensagem precisa de contexto de oportunidades"""
    m = message.lower()
    
    # Keywords que indicam pedido de oportunidades
    opportunity_keywords = [
        "jogo", "jogos", "hoje", "amanhã", "amanha",
        "oportunidade", "oportunidades", "aposta", "apostas",
        "odd", "odds", "entrada", "entradas", "sugestão", "sugestao",
        "múltipla", "multipla", "value", "ev", "+ev",
        "stake", "banca", "quanto apostar",
        "me mande", "me mostre", "quais são", "qual é", "quais", "qual",
        "tem algum", "tem alguma", "existe", "há"
    ]
    
    return any(k in m for k in opportunity_keywords)


def _build_context(bankroll: float) -> Dict:
    """Constrói contexto inteligente para o LLM usando APENAS cache"""
    from src.cache.daily_cache import DailyCache
    
    # 📦 USA APENAS O CACHE - NUNCA RECALCULA
    cached_data = DailyCache.load_today_data()
    
    if not cached_data:
        print("   ⚠️ Sem cache disponível - retornando vazio")
        return {
            'date': datetime.now().strftime('%d/%m/%Y'),
            'total_opportunities': 0,
            'total_games': 0,
            'opportunities': [],
            'games': [],
            'phase': 1,
            'bankroll': bankroll,
            'min_ev': 8.0
        }
    
    opportunities = cached_data['opportunities']
    
    # Organiza oportunidades por jogo
    games = {}
    for opp in opportunities:
        match_key = opp['match']
        if match_key not in games:
            games[match_key] = {
                'match': opp['match'],
                'competition': opp['competition'],
                'date': opp['date'],
                'opportunities': []
            }
        games[match_key]['opportunities'].append(opp)
    
    # Busca info da fase (isso não consome API)
    agent = BettingAgent(bankroll)
    phase_info = agent.bankroll_manager.get_phase_info()
    
    return {
        'date': datetime.now().strftime('%d/%m/%Y'),
        'total_opportunities': len(opportunities),
        'total_games': len(games),
        'opportunities': opportunities,
        'games': list(games.values()),
        'phase': phase_info['phase'],
        'bankroll': phase_info['bankroll'],
        'min_ev': phase_info['min_ev']
    }


# =========================
# Endpoints
# =========================
@app.get("/")
def read_root():
    return {"status": "online", "message": "Value Betting API"}


@app.post("/opportunities")
def get_opportunities(request: OpportunitiesRequest):
    """Retorna oportunidades do dia"""
    try:
        agent = BettingAgent(request.bankroll)
        opportunities = agent.analyze_today_opportunities()
        multiples = agent.detect_multiples(opportunities)

        return {
            "opportunities": opportunities,
            "multiples": multiples,
            "count": len(opportunities),
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n❌ ERRO NO OPPORTUNITIES:\n{error_detail}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
def get_statistics():
    """Retorna estatísticas"""
    try:
        agent = BettingAgent(100)
        stats = agent.get_statistics()
        return stats
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n❌ ERRO NO STATISTICS:\n{error_detail}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def get_history(limit: int = 10):
    """Retorna histórico de apostas"""
    try:
        bet_history = BetHistory()
        history = bet_history.get_recent_bets(limit)
        return history
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n❌ ERRO NO HISTORY:\n{error_detail}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phase")
def get_phase():
    """Retorna informações da fase atual"""
    try:
        agent = BettingAgent(100)
        phase_info = agent.bankroll_manager.get_phase_info()
        return phase_info
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n❌ ERRO NO PHASE:\n{error_detail}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(request: ChatRequest):
    """Endpoint de chat inteligente"""
    print(f"\n💬 Chat recebeu: {request.message}")
    
    needs_ctx = _needs_context(request.message)
    
    # Construi contexto apenas se necessário
    context = None
    if needs_ctx:
        print(f"   🔍 Detectado pedido de oportunidades - construindo contexto...")
        context = _build_context(bankroll=100.0)
        print(f"   📊 Contexto: {context['total_opportunities']} oportunidades em {context['total_games']} jogos")
        
        # Formata contexto para o LLM
        llm_context = {
            'bankroll': context['bankroll'],
            'phase': context['phase'],
            'opportunities': context['opportunities'],
            'stats': {}  # Pode adicionar stats se tiver
        }
    else:
        llm_context = None
    
    # Chama LLM com contexto estruturado
    try:
        response = llm_service.chat(
            user_message=request.message,
            context=llm_context
        )
        
        # ✅ CORRIGIDO: Retorna "message" ao invés de "response"
        return {"message": response}
    
    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        import traceback
        traceback.print_exc()
        return {
            "message": f"Desculpe, ocorreu um erro ao processar sua mensagem. Erro: {str(e)}"
        }


@app.post("/register-bet")
def register_bet(request: BetRequest):
    """Registra nova aposta"""
    try:
        agent = BettingAgent(100)
        bet_data = {
            "match": request.match,
            "market": request.market,
            "odds": request.odds,
            "stake": request.stake,
            "phase": request.phase,
        }
        bet_id = agent.register_bet(bet_data)
        return {"bet_id": bet_id, "message": "Aposta registrada com sucesso"}
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n❌ ERRO NO REGISTER-BET:\n{error_detail}\n")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)