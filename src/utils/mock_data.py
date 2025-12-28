from datetime import datetime, timedelta

def get_mock_matches():
    """Retorna jogos simulados para teste"""
    today = datetime.now()
    
    return [
        {
            'match_id': 1,
            'home_team': 'Flamengo',
            'away_team': 'Palmeiras',
            'competition': 'Brasileirão Série A',
            'date': (today + timedelta(hours=3)).isoformat(),
            'status': 'SCHEDULED'
        },
        {
            'match_id': 2,
            'home_team': 'Manchester City',
            'away_team': 'Arsenal',
            'competition': 'Premier League',
            'date': (today + timedelta(hours=5)).isoformat(),
            'status': 'SCHEDULED'
        },
        {
            'match_id': 3,
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'competition': 'La Liga',
            'date': (today + timedelta(hours=7)).isoformat(),
            'status': 'SCHEDULED'
        }
    ]

def get_mock_odds():
    """Retorna odds simuladas para teste"""
    return [
        {
            'match_id': 1,
            'home_team': 'Flamengo',
            'away_team': 'Palmeiras',
            'commence_time': datetime.now().isoformat(),
            'markets': {
                'over_2.5': 1.95,
                'under_2.5': 1.90,
                'btts_yes': 1.85,
                'btts_no': 2.00
            }
        },
        {
            'match_id': 2,
            'home_team': 'Manchester City',
            'away_team': 'Arsenal',
            'commence_time': datetime.now().isoformat(),
            'markets': {
                'over_2.5': 1.75,
                'under_2.5': 2.10,
                'btts_yes': 1.72,
                'btts_no': 2.15
            }
        },
        {
            'match_id': 3,
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'commence_time': datetime.now().isoformat(),
            'markets': {
                'over_2.5': 1.88,
                'under_2.5': 1.95,
                'btts_yes': 1.70,
                'btts_no': 2.20
            }
        }
    ]