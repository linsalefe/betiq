from src.models.bankroll_manager import BankrollManager
from src.models.probability_model import ProbabilityModel
from src.models.bet_history import BetHistory
from src.models.risk_manager import RiskManager
from src.models.advanced_stats import AdvancedStats
from src.services.football_api import FootballAPI
from src.services.api_football_service import APIFootballService
from src.utils.daily_cache import DailyCache
from src.services.team_matcher import TeamMatcher
from src.services.odds_api import OddsAPI
from src.utils.validators import OpportunityValidator
from src.utils.reporter import Reporter
from src.utils.multiple_detector import MultipleDetector
from typing import List, Dict

class BettingAgent:
    """Agente principal que orquestra análises e sugestões"""
    
    # 🎯 LIGAS OTIMIZADAS PARA MÁXIMO LUCRO
    PRIORITY_LEAGUES = [
        'soccer_epl',                      # Premier League (Inglaterra)
        'soccer_efl_champ',                # Championship (Inglaterra) ⭐ MELHOR VALUE
        'soccer_spain_la_liga',            # La Liga (Espanha)
        'soccer_germany_bundesliga',       # Bundesliga (Alemanha)
        'soccer_brazil_campeonato',        # Brasileirão Série A ⭐ ALTA INEFICIÊNCIA
        'soccer_italy_serie_a',            # Serie A (Itália)
        'soccer_portugal_primeira_liga',   # Primeira Liga (Portugal)
        'soccer_germany_bundesliga2'       # Bundesliga 2 (Alemanha) ⭐ BOM VALUE
    ]

    # Mapeamento de ligas The Odds API → Football-Data
    LEAGUE_MAPPING = {
        'soccer_epl': 'PL',                    # Premier League
        'soccer_italy_serie_a': 'SA',         # Serie A
        'soccer_portugal_primeira_liga': 'PPL', # Primeira Liga
        'soccer_spain_la_liga': 'PD',         # La Liga
        'soccer_germany_bundesliga': 'BL1',   # Bundesliga
        'soccer_brazil_campeonato': 'BSA',    # Brasileirão
    }

    def __init__(self, current_bankroll: float):
        """Inicializa o agente com a banca atual"""
        from src.models.bankroll_manager import BankrollManager
        
        self.bankroll_manager = BankrollManager(current_bankroll)
        self.probability_model = ProbabilityModel()
        self.football_api = FootballAPI()
        self.api_football = APIFootballService()
        self.odds_api = OddsAPI()
        self.bet_history = BetHistory()
        self.risk_manager = RiskManager(current_bankroll, self.bankroll_manager.phase)

    def analyze_today_opportunities(self) -> List[Dict]:
        """Analisa todas oportunidades do dia usando The Odds API + API-Football"""
        from config.config import Config
        
        print("🔍 Buscando oportunidades de hoje...")
        
        # 🎯 VERIFICA CACHE DIÁRIO PRIMEIRO
        cached_data = DailyCache.load_today_data()
        if and cached_data:  # FORÇANDO NOVA BUSCA
            print(f"   ✅ Já buscamos hoje! ({cached_data['matches_count']} jogos, {cached_data['leagues_count']} ligas)")
            print(f"   ✅ {len(cached_data['opportunities'])} oportunidades em cache")
            return cached_data['opportunities']
        
        print("   🆕 Primeira busca do dia - consultando APIs...")
        
        # 1. Busca jogos da API-Football (para ter IDs e stats)
        print("📊 Buscando jogos da API-Football...")
        api_football_matches = self.api_football.get_fixtures_next_days(1)  # Apenas hoje
        print(f"   ✅ {len(api_football_matches)} jogos encontrados (API-Football)")
        
        # 2. Busca odds da The Odds API (ligas prioritárias)
        print(f"💰 Buscando odds das {len(self.PRIORITY_LEAGUES)} ligas prioritárias...")
        print(f"   📋 Ligas: Championship, Premier, La Liga, Bundesliga, Brasileirão, Serie A, Portugal, Bundesliga 2")
        
        all_matches_with_odds = []
        leagues_found = 0
        
        for sport in self.PRIORITY_LEAGUES:
            try:
                matches = self.odds_api.get_odds_for_match(sport)
                if matches:
                    all_matches_with_odds.extend(matches)
                    leagues_found += 1
            except Exception as e:
                print(f"   ⚠️ Erro ao buscar {sport}: {e}")
                continue
        
        print(f"   ✅ {leagues_found} ligas carregadas")
        print(f"   ✅ {len(all_matches_with_odds)} jogos com odds disponíveis")

        # FILTRO: Remove jogos que não são de hoje/amanhã
        from datetime import datetime, timedelta
        today = datetime.now()
        max_date = today + timedelta(hours=12)
        
        filtered_matches = []
        for match in all_matches_with_odds:
            try:
                game_time_str = match.get('commence_time', '')
                if game_time_str:
                    # Parse da data
                    game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
                    game_time = game_time.replace(tzinfo=None)
                    
                    # Filtra jogos nas próximas 48h
                    if game_time <= max_date:
                        filtered_matches.append(match)
            except:
                continue
        
        all_matches_with_odds = filtered_matches
        print(f"   🗓️  Filtrado: {len(all_matches_with_odds)} jogos nas próximas 12h")
        
        if not all_matches_with_odds:
            if Config.ENVIRONMENT == 'production':
                print("❌ ERRO: Nenhum jogo com odds encontrado e sistema está em PRODUÇÃO")
                return []
            else:
                print("⚠️  Nenhum jogo encontrado. Usando dados simulados (DEVELOPMENT)...")
                from src.utils.mock_data import get_mock_matches, get_mock_odds
                matches = get_mock_matches()
                odds_data = get_mock_odds()
                # Processa dados simulados (fallback antigo)
                opportunities = []
                phase_info = self.bankroll_manager.get_phase_info()
                for match in matches:
                    match_odds = self._find_match_odds(match, odds_data)
                    if not match_odds:
                        continue
                    home_stats, away_stats = self._get_real_team_stats(match)
                    opps = self._analyze_match_markets(match, match_odds, phase_info, home_stats, away_stats)
                    opportunities.extend(opps)
                opportunities = self._validate_opportunities(opportunities, phase_info)
                opportunities.sort(key=lambda x: x['ev'], reverse=True)
                return opportunities
        
        # 3. Faz matching entre The Odds API e API-Football
        print(f"\n🔗 Fazendo matching entre APIs...")
        
        opportunities = []
        phase_info = self.bankroll_manager.get_phase_info()
        
        matched_count = 0
        total_processed = 0
        
        for match_with_odds in all_matches_with_odds:
            total_processed += 1
            
            # Tenta fazer match com API-Football
            matched_game = TeamMatcher.match_teams(
                match_with_odds['home_team'],
                match_with_odds['away_team'],
                api_football_matches,
                odds_datetime=match_with_odds.get('commence_time'),
                threshold=0.6
            )
            
            if matched_game:
                matched_count += 1
                
                # Usa dados do match (com IDs para buscar stats)
                match = {
                    'home_team': match_with_odds['home_team'],
                    'away_team': match_with_odds['away_team'],
                    'competition': match_with_odds.get('competition', matched_game.get('competition', 'N/A')),
                    'date': match_with_odds.get('commence_time', ''),
                    'league': match_with_odds.get('league', 'soccer_epl'),  # Liga do The Odds API
                    'home_team_id': matched_game.get('home_team_id'),
                    'away_team_id': matched_game.get('away_team_id'),
                    'league_id': matched_game.get('league_id')
                }
                
                if total_processed <= 3:  # Debug dos primeiros 3
                    print(f"   ✅ Match: {match_with_odds['home_team']} vs {match_with_odds['away_team']}")
                    print(f"      → {matched_game.get('home_team')} vs {matched_game.get('away_team')}")
                    print(f"      Score: {matched_game.get('match_score', 0):.2f} | IDs: {match['home_team_id']}, {match['away_team_id']}")
            else:
                # Sem match - usa dados da The Odds API sem IDs
                match = {
                    'home_team': match_with_odds['home_team'],
                    'away_team': match_with_odds['away_team'],
                    'competition': match_with_odds.get('competition', 'N/A'),
                    'date': match_with_odds.get('commence_time', ''),
                    'home_team_id': None,
                    'away_team_id': None,
                    'league_id': None
                }
                
                if total_processed <= 3:  # Debug dos primeiros 3
                    print(f"   ❌ Sem match: {match_with_odds['home_team']} vs {match_with_odds['away_team']}")
            
            # Busca estatísticas reais (vai usar APIs se tiver IDs, senão fallback)
            home_stats, away_stats = self._get_real_team_stats(match)
            
            # Analisa mercados (match_with_odds já tem as odds)
            opps = self._analyze_match_markets(match, match_with_odds, phase_info, home_stats, away_stats)
            opportunities.extend(opps)
        
        print(f"\n📊 RESULTADO DO MATCHING:")
        print(f"   ✅ {matched_count}/{total_processed} jogos com match ({matched_count/total_processed*100:.1f}%)")
        print(f"   ✅ {len(opportunities)} oportunidades encontradas (antes da validação)")
        
        # Valida oportunidades
        opportunities = self._validate_opportunities(opportunities, phase_info)
        
        print(f"   ✅ {len(opportunities)} oportunidades validadas")
        
        
        # Analisa Tênis
        print("\n🎾 Analisando oportunidades de Tênis...")
        tennis_opps = self.analyze_tennis_opportunities()
        if tennis_opps:
            opportunities.extend(tennis_opps)
            print(f"   ✅ {len(tennis_opps)} oportunidades de tênis adicionadas")
        
        # Ordena por EV
        opportunities.sort(key=lambda x: x['ev'], reverse=True)
        
        # 🎯 SALVA NO CACHE DIÁRIO
        DailyCache.save_today_data(
            opportunities=opportunities,
            matches_count=total_processed,
            leagues_count=leagues_found
        )
        
        return opportunities
    
    def _deduplicate_matches(self, matches: List[Dict]) -> List[Dict]:
        """Remove jogos duplicados (mesmo jogo de APIs diferentes)"""
        seen = set()
        unique = []
        
        for match in matches:
            # Cria chave única baseada nos times
            home = match['home_team'].lower().strip()
            away = match['away_team'].lower().strip()
            key = f"{home}|{away}"
            
            if key not in seen:
                seen.add(key)
                unique.append(match)
        
        return unique
    def detect_multiples(self, opportunities: List[Dict]) -> List[Dict]:
        """Detecta múltiplas estratégicas"""
        # Só sugere múltiplas em fase 1 e 2 (alavancagem agressiva)
        phase = self.bankroll_manager.phase
        
        if phase not in [1, 2]:
            return []
        
        # Detecta múltiplas
        multiples = MultipleDetector.detect_multiples(
            opportunities,
            min_combined_prob=0.30,  # 30% probabilidade combinada mínima
            max_legs=3  # Máximo 3 pernas
        )
        
        # Calcula stakes para cada múltipla
        formatted_multiples = []
        for multiple in multiples[:3]:  # Top 3 múltiplas
            # Stake mais agressivo para múltiplas (5-8% da banca)
            stake_pct = 0.08 if phase == 1 else 0.05
            stake = self.bankroll_manager.bankroll * stake_pct
            
            formatted = MultipleDetector.format_multiple(multiple, stake)
            formatted_multiples.append(formatted)
        
        return formatted_multiples
    
    def _validate_opportunities(self, opportunities: List[Dict], phase_info: Dict) -> List[Dict]:
        """Valida oportunidades antes de sugerir"""
        validated = []
        
        for opp in opportunities:
            is_valid, errors = OpportunityValidator.validate_opportunity(
                opp, 
                phase_info, 
                self.bankroll_manager.bankroll
            )
            
            if is_valid:
                # Verifica limites de risco
                can_bet, msg = self.risk_manager.check_daily_limit(opp['stake'])
                if can_bet:
                    validated.append(opp)
                else:
                    print(f"⚠️  Rejeitado: {opp['match']} - {msg}")
            else:
                print(f"⚠️  Rejeitado: {opp['match']} - {errors[0]}")
        
        return validated
    
    def _find_match_odds(self, match: Dict, odds_data: List[Dict]) -> Dict:
        """Encontra odds para o jogo específico"""
        # DEBUG: Mostra apenas os primeiros 3 matchings
        if not hasattr(self, '_match_debug_count'):
            self._match_debug_count = 0
        
        if self._match_debug_count < 3:
            print(f"\n🔍 Tentando matchear: {match['home_team']} vs {match['away_team']}")
            self._match_debug_count += 1
        
        for odds in odds_data:
            home_match = odds['home_team'].lower() in match['home_team'].lower()
            away_match = odds['away_team'].lower() in match['away_team'].lower()
            
            if self._match_debug_count <= 3 and (home_match or away_match):
                print(f"   🎯 Candidato: {odds['home_team']} vs {odds['away_team']}")
                print(f"      Home match: {home_match} | Away match: {away_match}")
            
            if home_match or away_match:
                return odds
        
        if self._match_debug_count <= 3:
            print(f"   ❌ Nenhuma odd encontrada para este jogo")
            print(f"   📋 Exemplo de odd disponível: {odds_data[0]['home_team']} vs {odds_data[0]['away_team']}")
        
        return {}
    
    def _get_real_team_stats(self, match: Dict) -> tuple:
        """
        Busca estatísticas reais dos times via Football-Data API
        Retorna (home_stats, away_stats) com stats de CASA e FORA
        """
        print(f"\n🔎 Buscando stats reais: {match.get('home_team')} vs {match.get('away_team')}")
        
        home_team_name = match.get('home_team')
        away_team_name = match.get('away_team')
        league = match.get('league', 'soccer_epl')  # Liga do jogo
        
        # Mapeia liga para código Football-Data
        competition_code = self.LEAGUE_MAPPING.get(league, 'PL')
        print(f"   📍 Liga: {league} → {competition_code}")
        
        # Busca IDs dos times no Football-Data
        home_team_id = self.football_api.get_team_id_by_name(home_team_name, competition_code)
        away_team_id = self.football_api.get_team_id_by_name(away_team_name, competition_code)
        
        if not home_team_id or not away_team_id:
            print(f"   ❌ IDs não encontrados em {competition_code}!")
            return None, None
        
        print(f"   ✅ IDs encontrados: {home_team_id}, {away_team_id}")
        
        # Busca stats separadas por venue (casa/fora)
        home_stats_data = self.football_api.get_team_stats_by_venue(home_team_id, season=2025)
        away_stats_data = self.football_api.get_team_stats_by_venue(away_team_id, season=2025)
        
        if not home_stats_data or not away_stats_data:
            print(f"   ❌ Stats não disponíveis no Football-Data")
            return None, None
        
        # Time mandante joga EM CASA
        home_venue_stats = home_stats_data['home']
        # Time visitante joga FORA
        away_venue_stats = away_stats_data['away']
        
        print(f"   ✅ Stats reais carregadas!")
        print(f"      🏠 {home_team_name} (casa): {home_venue_stats['avg_scored']:.2f} marcados / {home_venue_stats['avg_conceded']:.2f} sofridos")
        print(f"      🚗 {away_team_name} (fora): {away_venue_stats['avg_scored']:.2f} marcados / {away_venue_stats['avg_conceded']:.2f} sofridos")
        
        # Monta dados para cálculo ajustado
        home_team_data = {
            'base_avg_scored': home_venue_stats['avg_scored'],
            'base_avg_conceded': home_venue_stats['avg_conceded'],
            'recent_form': ['W', 'W', 'W', 'W', 'W'],
            'is_home': True
        }
        
        away_team_data = {
            'base_avg_scored': away_venue_stats['avg_scored'],
            'base_avg_conceded': away_venue_stats['avg_conceded'],
            'recent_form': ['W', 'W', 'W', 'W', 'W'],
            'is_home': False
        }
        
        home_stats_final = self._calculate_adjusted_stats(home_team_data)
        away_stats_final = self._calculate_adjusted_stats(away_team_data)
        
        return home_stats_final, away_stats_final
    def _calculate_adjusted_stats(self, team_data: Dict) -> Dict:
        """Calcula estatísticas ajustadas com forma recente e mando de campo"""
        base_scored = team_data.get('base_avg_scored', 1.5)
        base_conceded = team_data.get('base_avg_conceded', 1.3)
        recent_form = team_data.get('recent_form', [])
        is_home = team_data.get('is_home', False)
        
        # Ajuste por forma recente (últimos 5 jogos)
        form_adjustment = 1.0
        if recent_form:
            wins = recent_form.count('W')
            losses = recent_form.count('L')
            if wins >= 3:
                form_adjustment = 1.15  # +15% se boa forma
            elif losses >= 3:
                form_adjustment = 0.85  # -15% se má forma
        
        # Ajuste por mando de campo
        home_adjustment = 1.1 if is_home else 0.9
        
        # Aplica ajustes
        adjusted_scored = base_scored * form_adjustment * home_adjustment
        adjusted_conceded = base_conceded / form_adjustment / home_adjustment
        
        return {
            'avg_scored': adjusted_scored,
            'avg_conceded': adjusted_conceded
        }
    
    def _expected_goals(self, home_stats: Dict, away_stats: Dict) -> tuple:
        """
        Calcula expectativa de gols usando ataque vs defesa
        
        Returns:
            (home_lambda, away_lambda) - Expectativa de gols de cada time
        """
        home_lambda = (home_stats['avg_scored'] + away_stats['avg_conceded']) / 2
        away_lambda = (away_stats['avg_scored'] + home_stats['avg_conceded']) / 2
        
        return home_lambda, away_lambda
    
    def _analyze_match_markets(self, match: Dict, odds: Dict, phase_info: Dict, 
                               home_stats: Dict, away_stats: Dict) -> List[Dict]:
        """Analisa mercados disponíveis do jogo"""
        opportunities = []
        markets = odds.get('markets', {})
        
        # Verifica se tem stats reais
        if not home_stats or not away_stats:
            print(f"   ⚠️  Pulando {match.get('home_team')} x {match.get('away_team')} - sem stats reais")
            return []
        
        # DEBUG: Força debug nos primeiros 5 jogos
        if not hasattr(self, '_debug_count'):
            self._debug_count = 0
        
        should_debug = self._debug_count < 5
        self._debug_count += 1
        
        if should_debug:
            print(f"\n🎯 DEBUG #{self._debug_count}: {match['home_team']} x {match['away_team']}")
            print(f"   📊 Home: {home_stats['avg_scored']:.2f} gols/jogo | Away: {away_stats['avg_scored']:.2f} gols/jogo")
            print(f"   📊 EV mínimo exigido: {phase_info['min_ev']}%")
        
        # DEBUG: Mostra estrutura de markets
        if should_debug:
            if 'over_2.5' in markets:
                print(f"   🔍 markets['over_2.5']: {markets['over_2.5']}")
            if 'spread_-0.5' in markets:
                print(f"   🔍 markets['spread_-0.5']: {markets['spread_-0.5']}")
            if 'spread_0.5' in markets:
                print(f"   🔍 markets['spread_0.5']: {markets['spread_0.5']}")
        
        # 1. Over 2.5
        if 'over_2.5' in markets:
            opp = self._analyze_over(match, odds, home_stats, away_stats, 2.5, markets['over_2.5'], phase_info)
            if opp:
                opportunities.append(opp)
                if should_debug:
                    print(f"   ✅ Over 2.5 @ {markets['over_2.5']} - EV: {opp['ev']:.1f}% - Prob: {opp['probability']*100:.1f}%")
            elif should_debug:
                # Calcula manualmente para debug
                probs = self.probability_model.calculate_over_under(home_stats['avg_scored'], away_stats['avg_scored'], 2.5)
                is_valid, ev = self.probability_model.validate_opportunity(probs['prob_over'], markets['over_2.5'], phase_info['min_ev'])
                print(f"   ❌ Over 2.5 @ {markets['over_2.5']} - EV: {ev:.1f}% - Prob: {probs['prob_over']*100:.1f}%")
        
        # 2. Under 2.5
        if 'under_2.5' in markets:
            opp = self._analyze_under(match, odds, home_stats, away_stats, 2.5, markets['under_2.5'], phase_info)
            if opp:
                opportunities.append(opp)
                if should_debug:
                    print(f"   ✅ Under 2.5 @ {markets['under_2.5']} - EV: {opp['ev']:.1f}% - Prob: {opp['probability']*100:.1f}%")
            elif should_debug:
                probs = self.probability_model.calculate_over_under(home_stats['avg_scored'], away_stats['avg_scored'], 2.5)
                is_valid, ev = self.probability_model.validate_opportunity(probs['prob_under'], markets['under_2.5'], phase_info['min_ev'])
                print(f"   ❌ Under 2.5 @ {markets['under_2.5']} - EV: {ev:.1f}% - Prob: {probs['prob_under']*100:.1f}%")
        
        # 3. Handicaps
        handicap_count = 0
        for spread_key in markets.keys():
            if spread_key.startswith('spread_'):
                parts = spread_key.split('_')
                if len(parts) >= 2:
                    try:
                        handicap = float(parts[1])
                        opp = self._analyze_handicap(match, odds, home_stats, away_stats, handicap, markets[spread_key], phase_info)
                        if opp:
                            opportunities.append(opp)
                            if should_debug and handicap_count < 2:
                                print(f"   ✅ Handicap {handicap:+.1f} @ {markets[spread_key]} - EV: {opp['ev']:.1f}%")
                                handicap_count += 1
                    except ValueError:
                        continue
        
        # 4. BTTS (se disponível)
        if 'btts_yes' in markets:
            opp = self._analyze_btts(match, odds, home_stats, away_stats, markets['btts_yes'], phase_info)
            if opp:
                opportunities.append(opp)
                if should_debug:
                    print(f"   ✅ BTTS @ {markets['btts_yes']} - EV: {opp['ev']:.1f}%")
        
        return opportunities
    
    def _analyze_over(self, match: Dict, odds: Dict, home_stats: Dict, 
                     away_stats: Dict, line: float, market_odds, 
                     phase_info: Dict) -> Dict:
        """Analisa oportunidade de Over usando lambdas"""
        
        # Extrai odd e bookmaker
        if isinstance(market_odds, dict):
            bookmaker = market_odds.get("bookmaker", "Unknown")
            market_odds = market_odds.get("odd", market_odds)
        else:
            bookmaker = "Unknown"
        
        # Calcula lambdas (ataque vs defesa)
        home_lambda, away_lambda = self._expected_goals(home_stats, away_stats)
        
        # 🎯 FILTRO 1: Over 2.5 precisa de 3.2+ gols esperados
        expected_goals = home_lambda + away_lambda
        if line == 2.5 and expected_goals < 3.2:
            if hasattr(self, '_debug_count') and self._debug_count <= 5:
                print(f"   ❌ Over {line} rejeitado: apenas {expected_goals:.2f} gols esperados (mín: 3.2)")
            return None
        
        # Calcula probabilidades usando lambdas
        probs = self.probability_model.calculate_over_under(home_lambda, away_lambda, line)
        
        # 🎯 FILTRO 2: EV mínimo de +25%
        min_ev_required = max(phase_info['min_ev'], 0.25)  # No mínimo 25%
        
        is_valid, ev = self.probability_model.validate_opportunity(
            probs['prob_over'], 
            market_odds, 
            min_ev_required
        )

        is_valid, ev = self.probability_model.validate_opportunity(
            probs['prob_over'], 
            market_odds, 
            phase_info['min_ev']
        )
        
        if not is_valid:
            return None
        
        stake = self.bankroll_manager.calculate_stake(
            probs['prob_over'], 
            market_odds, 
            ev
        )
        
        # Aplica ajuste de risco
        stake_adjustment = self.risk_manager.get_stake_adjustment()
        stake = stake * stake_adjustment
        
        return {
            'match': f"{match['home_team']} x {match['away_team']}",
            'competition': match.get('competition', 'N/A'),
            'date': match['date'],
            'market': f'Over {line}',
            'odds': market_odds,
            'bookmaker': bookmaker,
            'probability': probs['prob_over'],
            'ev': ev,
            'stake': round(stake, 2),
            'potential_return': round(stake * market_odds, 2),
            'phase': phase_info['phase']
        }
    
    def _analyze_under(self, match: Dict, odds: Dict, home_stats: Dict, 
                      away_stats: Dict, line: float, market_odds, 
                      phase_info: Dict) -> Dict:
        """Analisa oportunidade de Under usando lambdas"""
        
        # Extrai odd e bookmaker
        if isinstance(market_odds, dict):
            bookmaker = market_odds.get("bookmaker", "Unknown")
            market_odds = market_odds.get("odd", market_odds)
        else:
            bookmaker = "Unknown"
        
        # Calcula lambdas (ataque vs defesa)
        home_lambda, away_lambda = self._expected_goals(home_stats, away_stats)
        
        # Calcula probabilidades usando lambdas
        probs = self.probability_model.calculate_over_under(home_lambda, away_lambda, line)
        
        # Usa probabilidade de UNDER
        is_valid, ev = self.probability_model.validate_opportunity(
            probs['prob_under'], 
            market_odds, 
            phase_info['min_ev']
        )
        
        if not is_valid:
            return None
        
        stake = self.bankroll_manager.calculate_stake(
            probs['prob_under'], 
            market_odds, 
            ev
        )
        
        # Aplica ajuste de risco
        stake_adjustment = self.risk_manager.get_stake_adjustment()
        stake = stake * stake_adjustment
        
        return {
            'match': f"{match['home_team']} x {match['away_team']}",
            'competition': match.get('competition', 'N/A'),
            'date': match['date'],
            'market': f'Under {line}',
            'odds': market_odds,
            'bookmaker': bookmaker,
            'probability': probs['prob_under'],
            'ev': ev,
            'stake': round(stake, 2),
            'potential_return': round(stake * market_odds, 2),
            'phase': phase_info['phase']
        }
    
    def _analyze_handicap(self, match: Dict, odds: Dict, home_stats: Dict, 
                         away_stats: Dict, line: float, market_odds, 
                         phase_info: Dict) -> Dict:
        """Analisa oportunidade de Handicap/Spread usando lambdas"""
        
        # Extrai odd e bookmaker
        if isinstance(market_odds, dict):
            bookmaker = market_odds.get("bookmaker", "Unknown")
            market_odds = market_odds.get("odd", market_odds)
        else:
            bookmaker = "Unknown"
        
        # Calcula lambdas (ataque vs defesa)
        home_lambda, away_lambda = self._expected_goals(home_stats, away_stats)
        
        # Calcula probabilidades usando lambdas
        probs = self.probability_model.calculate_handicap(home_lambda, away_lambda, line)
        
        is_valid, ev = self.probability_model.validate_opportunity(
            probs['prob_home_cover'], 
            market_odds, 
            phase_info['min_ev']
        )
        
        if not is_valid:
            return None
        
        stake = self.bankroll_manager.calculate_stake(
            probs['prob_home_cover'], 
            market_odds, 
            ev
        )
        
        # Aplica ajuste de risco
        stake_adjustment = self.risk_manager.get_stake_adjustment()
        stake = stake * stake_adjustment
        
        line_str = f"{line:+.1f}" if line != 0 else "0.0"
        
        return {
            'match': f"{match['home_team']} x {match['away_team']}",
            'competition': match.get('competition', 'N/A'),
            'date': match['date'],
            'market': f"{match['home_team']} {line_str}",
            'odds': market_odds,
            'bookmaker': bookmaker,
            'probability': probs['prob_home_cover'],
            'ev': ev,
            'stake': round(stake, 2),
            'potential_return': round(stake * market_odds, 2),
            'phase': phase_info['phase']
        }
    
    def _analyze_btts(self, match: Dict, odds: Dict, home_stats: Dict, 
                     away_stats: Dict, market_odds, phase_info: Dict) -> Dict:
        """Analisa oportunidade de BTTS (Both Teams To Score) usando lambdas"""
        
        # Extrai odd e bookmaker
        if isinstance(market_odds, dict):
            bookmaker = market_odds.get("bookmaker", "Unknown")
            market_odds = market_odds.get("odd", market_odds)
        else:
            bookmaker = "Unknown"
        
        # Calcula lambdas (ataque vs defesa)
        home_lambda, away_lambda = self._expected_goals(home_stats, away_stats)
        
        # Calcula probabilidade de BTTS usando lambdas
        prob_btts = self.probability_model.calculate_btts_from_lambdas(home_lambda, away_lambda)
        
        is_valid, ev = self.probability_model.validate_opportunity(
            prob_btts, 
            market_odds, 
            phase_info['min_ev']
        )
        
        if not is_valid:
            return None
        
        stake = self.bankroll_manager.calculate_stake(prob_btts, market_odds, ev)
        
        # Aplica ajuste de risco
        stake_adjustment = self.risk_manager.get_stake_adjustment()
        stake = stake * stake_adjustment
        
        return {
            'match': f"{match['home_team']} x {match['away_team']}",
            'competition': match.get('competition', 'N/A'),
            'date': match['date'],
            'market': 'BTTS (Ambas Marcam)',
            'odds': market_odds,
            'probability': prob_btts,
            'ev': ev,
            'stake': round(stake, 2),
            'potential_return': round(stake * market_odds, 2),
            'phase': phase_info['phase']
        }
    
    def register_bet(self, bet_data: Dict) -> str:
        """Registra aposta no histórico"""
        bet_id = self.bet_history.add_bet(bet_data)
        self.risk_manager.add_stake(bet_data['stake'])
        return bet_id
    
    def update_bet_result(self, bet_id: str, result: str):
        """Atualiza resultado de aposta"""
        success = self.bet_history.update_bet_result(bet_id, result)
        if success:
            self.risk_manager.update_sequence(result)
        return success
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas completas"""
        return self.bet_history.get_statistics(self.bankroll_manager.phase)
    
    def check_phase_completion(self) -> tuple:
        """Verifica se completou fase"""
        return self.bankroll_manager.check_phase_completion()
    
    def get_full_report(self, opportunities: List[Dict]) -> str:
        """Gera relatório completo"""
        phase_info = self.bankroll_manager.get_phase_info()
        risk_summary = self.risk_manager.get_risk_summary()
        
        report = Reporter.generate_daily_report(opportunities, phase_info, risk_summary)
        
        if opportunities:
            report += Reporter.format_opportunity_list(opportunities)
            
            # Detecta e mostra múltiplas
            multiples = self.detect_multiples(opportunities)
            if multiples:
                report += "\n🎯 MÚLTIPLAS ESTRATÉGICAS DETECTADAS:\n"
                for i, multiple in enumerate(multiples, 1):
                    report += Reporter.format_multiple_suggestion(multiple)
        
        # Verifica se completou fase
        completed, withdraw = self.check_phase_completion()
        if completed:
            report += Reporter.generate_phase_completion_alert(
                phase_info['phase'],
                withdraw,
                self.bankroll_manager.bankroll - withdraw
            )
        
        # Adiciona estatísticas
        stats = self.get_statistics()
        if stats['total_bets'] > 0:
            report += Reporter.generate_statistics_report(stats)
        
        return report
    
    def get_phase_summary(self) -> str:
        """Retorna resumo da fase atual"""
        info = self.bankroll_manager.get_phase_info()
        
        if info['phase'] == 'Consolidação':
            return f"""
✅ MODO CONSOLIDAÇÃO
Banca atual: R$ {info['bankroll']:.2f}
EV mínimo: {info['min_ev']}%
Stake máximo: {info['max_stake_pct']}%
"""
        
        return f"""
🚀 FASE {info['phase']}: ALAVANCAGEM
Banca atual: R$ {info['bankroll']:.2f}
Meta: R$ {info['target']:.2f}
Progresso: {info['progress']:.1f}%
Faltam: R$ {info['remaining']:.2f}
EV mínimo: {info['min_ev']}%
Stake máximo: {info['max_stake_pct']}%
"""
    def analyze_tennis_opportunities(self) -> List[Dict]:
        """Analisa oportunidades de apostas em Tênis"""
        try:
            from src.services.tennis_api import TennisAPI
            from src.models.tennis_probability_model import TennisProbabilityModel
            
            print("\n🎾 === ANALISANDO TÊNIS ===")
            
            tennis_api = TennisAPI()
            tennis_model = TennisProbabilityModel()
            opportunities = []
            
            # Busca partidas ao vivo
            matches = tennis_api.get_live_matches()
            
            if not matches:
                print("ℹ️ Nenhuma partida de tênis ao vivo no momento")
                return []
            
            print(f"📊 Analisando {len(matches)} partidas de tênis...")
            
            for match in matches:
                player1_name = match.get('player1', 'Unknown')
                player2_name = match.get('player2', 'Unknown')
                tour = match.get('tour', 'ATP')
                
                # Busca stats dos jogadores
                player1_stats = tennis_api.get_player_stats_from_ranking(player1_name, tour)
                player2_stats = tennis_api.get_player_stats_from_ranking(player2_name, tour)
                
                # Calcula probabilidade
                prob = tennis_model.calculate_match_winner(
                    player1_win_rate=player1_stats['estimated_win_rate'],
                    player2_win_rate=player2_stats['estimated_win_rate'],
                    surface=match.get('surface', 'Hard')
                )
                
                # Aqui você integraria com Odds API para buscar odds reais
                # Por enquanto, registra a análise
                opportunities.append({
                    'sport': 'Tennis',
                    'match': f"{player1_name} vs {player2_name}",
                    'tournament': match.get('tournament', 'Unknown'),
                    'player1_prob': prob['prob_player1_win'],
                    'player2_prob': prob['prob_player2_win'],
                    'player1_rank': player1_stats['rank'],
                    'player2_rank': player2_stats['rank'],
                })
            
            print(f"✅ {len(opportunities)} partidas de tênis analisadas")
            return opportunities
            
        except Exception as e:
            print(f"⚠️ Erro ao analisar tênis: {e}")
            return []
