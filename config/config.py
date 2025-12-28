import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações gerais do agente"""
    
    # Ambiente
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Banca
    INITIAL_BANKROLL = float(os.getenv('INITIAL_BANKROLL', 100))
    CURRENT_PHASE = int(os.getenv('CURRENT_PHASE', 1))
    CONSOLIDATION_THRESHOLD = float(os.getenv('CONSOLIDATION_THRESHOLD', 50000))
    
    # Metas por fase
    PHASE_TARGETS = {
        1: float(os.getenv('TARGET_BANKROLL_PHASE_1', 1000)),
        2: float(os.getenv('TARGET_BANKROLL_PHASE_2', 5000)),
        3: float(os.getenv('TARGET_BANKROLL_PHASE_3', 25000)),
        4: float(os.getenv('TARGET_BANKROLL_PHASE_4', 100000))
    }
    
    # EV mínimo por fase
    MIN_EV = {
        1: float(os.getenv('MIN_EV_PHASE_1', 8)),
        2: float(os.getenv('MIN_EV_PHASE_2', 9)),
        3: float(os.getenv('MIN_EV_PHASE_3', 10)),
        4: float(os.getenv('MIN_EV_PHASE_4', 12)),
        'consolidation': float(os.getenv('MIN_EV_CONSOLIDATION', 12))
    }
    
    # Stake máximo por fase (%)
    MAX_STAKE = {
        1: float(os.getenv('MAX_STAKE_PHASE_1', 15)),
        2: float(os.getenv('MAX_STAKE_PHASE_2', 10)),
        3: float(os.getenv('MAX_STAKE_PHASE_3', 6)),
        4: float(os.getenv('MAX_STAKE_PHASE_4', 4)),
        'consolidation': float(os.getenv('MAX_STAKE_CONSOLIDATION', 1.5))
    }
    
    # APIs
    FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')
    FOOTBALL_API_BASE_URL = os.getenv('FOOTBALL_API_BASE_URL')
    ODDS_API_KEY = os.getenv('ODDS_API_KEY')
    ODDS_API_BASE_URL = os.getenv('ODDS_API_BASE_URL')
    
    # API-Football (api-sports.io)
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
    API_FOOTBALL_BASE_URL = os.getenv('API_FOOTBALL_BASE_URL')
    
    # Database
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', 5432),
        'database': os.getenv('DB_NAME', 'agente_betting'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD')
    }    
    # NFL
    NFL_ENABLED = os.getenv('NFL_ENABLED', 'False') == 'True'
    ESPN_NFL_BASE_URL = os.getenv('ESPN_NFL_BASE_URL', 'https://site.api.espn.com/apis/site/v2/sports/football/nfl')
    NFL_MIN_EV = float(os.getenv('NFL_MIN_EV', 8))
    NFL_HOME_ADVANTAGE = float(os.getenv('NFL_HOME_ADVANTAGE', 2.5))
    
    # Tennis
    TENNIS_ENABLED = os.getenv('TENNIS_ENABLED', 'False') == 'True'
    TENNIS_MIN_EV = float(os.getenv('TENNIS_MIN_EV', 8))
    
    # RapidAPI Tennis
    RAPIDAPI_TENNIS_KEY = os.getenv('RAPIDAPI_TENNIS_KEY')
