import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config.config import Config
from src.cache.redis_client import RedisCache


class APIFootballService:
    """Serviço para API-Football (api-sports.io) com estatísticas avançadas"""
    
    def __init__(self):
        self.api_key = Config.API_FOOTBALL_KEY
        self.base_url = Config.API_FOOTBALL_BASE_URL
        self.cache = RedisCache()
    
    def get_fixtures_by_date(self, date: str) -> List[Dict]:
        """
        Busca jogos de uma data específica
        Args:
            date: Data no formato YYYY-MM-DD
        """
        cache_key = f"api_football_fixtures_{date}"
        
        # Verifica cache
        cached = self.cache.get(cache_key)
        if cached:
            print(f"📦 Usando cache (API-Football {date})")
            return cached
        
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/fixtures"
        headers = {
            'x-apisports-key': self.api_key
        }
        params = {
            'date': date
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            fixtures = self._format_fixtures(data.get('response', []))
            
            # Cache por 6 horas
            self.cache.set(cache_key, fixtures, expire_seconds=21600)
            
            return fixtures
            
        except Exception as e:
            print(f"❌ Erro ao buscar fixtures da API-Football: {e}")
            return []
    
    def get_fixtures_next_days(self, days: int = 3) -> List[Dict]:
        """Busca jogos dos próximos N dias"""
        all_fixtures = []
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            fixtures = self.get_fixtures_by_date(date)
            all_fixtures.extend(fixtures)
        
        return all_fixtures
    
    def get_team_statistics(self, team_id: int, league_id: int, season: int) -> Optional[Dict]:
        """
        Busca estatísticas detalhadas de um time em uma liga/temporada
        Retorna: avg_scored, avg_conceded, wins, draws, losses, etc
        """
        cache_key = f"api_football_team_stats_{team_id}_{league_id}_{season}"
        
        # Verifica cache (24 horas)
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/teams/statistics"
        headers = {
            'x-apisports-key': self.api_key
        }
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('response'):
                return None
            
            stats = self._extract_team_statistics(data['response'])
            
            # Cache por 24 horas
            self.cache.set(cache_key, stats, expire_seconds=86400)
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar estatísticas do time {team_id}: {e}")
            return None
    
    def get_team_form(self, team_id: int, last_n_games: int = 5) -> List[str]:
        """
        Busca forma recente do time (últimos N jogos)
        Retorna: ['W', 'L', 'D', 'W', 'W']
        """
        cache_key = f"api_football_team_form_{team_id}_{last_n_games}"
        
        # Verifica cache (6 horas)
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        if not self.api_key:
            return ['D'] * last_n_games  # Retorna empates como fallback
        
        url = f"{self.base_url}/fixtures"
        headers = {
            'x-apisports-key': self.api_key
        }
        params = {
            'team': team_id,
            'last': last_n_games
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            form = []
            for fixture in data.get('response', []):
                result = self._get_match_result(fixture, team_id)
                if result:
                    form.append(result)
            
            # Cache por 6 horas
            self.cache.set(cache_key, form, expire_seconds=21600)
            
            return form
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar forma do time {team_id}: {e}")
            return ['D'] * last_n_games
    
    def get_head_to_head(self, team1_id: int, team2_id: int, last_n: int = 5) -> Dict:
        """
        Busca confrontos diretos entre dois times
        Retorna estatísticas dos últimos confrontos
        """
        cache_key = f"api_football_h2h_{team1_id}_{team2_id}_{last_n}"
        
        # Verifica cache (24 horas)
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        if not self.api_key:
            return {'team1_wins': 0, 'team2_wins': 0, 'draws': 0}
        
        url = f"{self.base_url}/fixtures/headtohead"
        headers = {
            'x-apisports-key': self.api_key
        }
        params = {
            'h2h': f"{team1_id}-{team2_id}",
            'last': last_n
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            h2h_stats = self._analyze_h2h(data.get('response', []), team1_id, team2_id)
            
            # Cache por 24 horas
            self.cache.set(cache_key, h2h_stats, expire_seconds=86400)
            
            return h2h_stats
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar H2H: {e}")
            return {'team1_wins': 0, 'team2_wins': 0, 'draws': 0}
    
    def _format_fixtures(self, fixtures: List[Dict]) -> List[Dict]:
        """Formata fixtures para padrão interno"""
        formatted = []
        
        for fixture in fixtures:
            # Filtra apenas jogos futuros ou ao vivo
            status = fixture.get('fixture', {}).get('status', {}).get('short')
            if status not in ['NS', 'TBD', '1H', '2H', 'HT', 'LIVE']:
                continue
            
            fixture_data = fixture.get('fixture', {})
            teams = fixture.get('teams', {})
            league = fixture.get('league', {})
            
            formatted_fixture = {
                'match_id': f"apif_{fixture_data.get('id')}",
                'home_team': teams.get('home', {}).get('name', ''),
                'away_team': teams.get('away', {}).get('name', ''),
                'competition': league.get('name', 'Unknown'),
                'date': fixture_data.get('date', ''),
                'status': status,
                'source': 'api-football',
                'league_id': league.get('id'),
                'home_team_id': teams.get('home', {}).get('id'),
                'away_team_id': teams.get('away', {}).get('id')
            }
            
            formatted.append(formatted_fixture)
        
        return formatted
    
    def _extract_team_statistics(self, response: Dict) -> Dict:
        """Extrai estatísticas relevantes da resposta da API"""
        fixtures = response.get('fixtures', {})
        goals = response.get('goals', {})
        
        # Jogos totais
        played = fixtures.get('played', {}).get('total', 0)
        if played == 0:
            played = 1  # Evita divisão por zero
        
        # Gols marcados
        scored_total = goals.get('for', {}).get('total', {}).get('total', 0)
        avg_scored = scored_total / played
        
        # Gols sofridos
        conceded_total = goals.get('against', {}).get('total', {}).get('total', 0)
        avg_conceded = conceded_total / played
        
        # Vitórias, empates, derrotas
        wins = fixtures.get('wins', {}).get('total', 0)
        draws = fixtures.get('draws', {}).get('total', 0)
        losses = fixtures.get('loses', {}).get('total', 0)
        
        # Desempenho em casa vs fora
        home_avg_scored = 0
        home_avg_conceded = 0
        away_avg_scored = 0
        away_avg_conceded = 0
        
        home_played = fixtures.get('played', {}).get('home', 0)
        away_played = fixtures.get('played', {}).get('away', 0)
        
        if home_played > 0:
            home_scored = goals.get('for', {}).get('total', {}).get('home', 0)
            home_conceded = goals.get('against', {}).get('total', {}).get('home', 0)
            home_avg_scored = home_scored / home_played
            home_avg_conceded = home_conceded / home_played
        
        if away_played > 0:
            away_scored = goals.get('for', {}).get('total', {}).get('away', 0)
            away_conceded = goals.get('against', {}).get('total', {}).get('away', 0)
            away_avg_scored = away_scored / away_played
            away_avg_conceded = away_conceded / away_played
        
        return {
            'avg_scored': round(avg_scored, 2),
            'avg_conceded': round(avg_conceded, 2),
            'home_avg_scored': round(home_avg_scored, 2),
            'home_avg_conceded': round(home_avg_conceded, 2),
            'away_avg_scored': round(away_avg_scored, 2),
            'away_avg_conceded': round(away_avg_conceded, 2),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'played': played
        }
    
    def _get_match_result(self, fixture: Dict, team_id: int) -> Optional[str]:
        """Retorna 'W', 'L' ou 'D' para o time específico"""
        if fixture.get('fixture', {}).get('status', {}).get('short') not in ['FT', 'AET', 'PEN']:
            return None
        
        teams = fixture.get('teams', {})
        goals = fixture.get('goals', {})
        
        home_id = teams.get('home', {}).get('id')
        away_id = teams.get('away', {}).get('id')
        home_goals = goals.get('home', 0)
        away_goals = goals.get('away', 0)
        
        if home_goals == away_goals:
            return 'D'
        
        if team_id == home_id:
            return 'W' if home_goals > away_goals else 'L'
        elif team_id == away_id:
            return 'W' if away_goals > home_goals else 'L'
        
        return None
    
    def _analyze_h2h(self, fixtures: List[Dict], team1_id: int, team2_id: int) -> Dict:
        """Analisa confrontos diretos"""
        team1_wins = 0
        team2_wins = 0
        draws = 0
        
        for fixture in fixtures:
            if fixture.get('fixture', {}).get('status', {}).get('short') not in ['FT', 'AET', 'PEN']:
                continue
            
            teams = fixture.get('teams', {})
            goals = fixture.get('goals', {})
            
            home_id = teams.get('home', {}).get('id')
            home_goals = goals.get('home', 0)
            away_goals = goals.get('away', 0)
            
            if home_goals == away_goals:
                draws += 1
            elif home_id == team1_id:
                if home_goals > away_goals:
                    team1_wins += 1
                else:
                    team2_wins += 1
            else:
                if away_goals > home_goals:
                    team1_wins += 1
                else:
                    team2_wins += 1
        
        return {
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'total_games': team1_wins + team2_wins + draws
        }