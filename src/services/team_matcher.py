from difflib import SequenceMatcher
from typing import Optional, Dict, List
from datetime import datetime, timedelta


class TeamMatcher:
    """Serviço para fazer matching inteligente entre nomes de times de diferentes APIs"""
    
    # Mapeamento manual de abreviações conhecidas
    KNOWN_MAPPINGS = {
        # Premier League
        "man utd": "manchester united",
        "man united": "manchester united",
        "man city": "manchester city",
        "spurs": "tottenham",
        "tottenham hotspur": "tottenham",
        
        # La Liga
        "athletic bilbao": "athletic club",
        "athletic club": "athletic bilbao",
        
        # Serie A
        "ac milan": "milan",
        "inter milan": "inter",
        
        # Bundesliga
        "bayern munich": "bayern munchen",
        "bayern munchen": "bayern munich",
        
        # Portugal
        "sporting lisbon": "sporting cp",
        "sporting cp": "sporting lisbon",
        "sporting clube de portugal": "sporting cp",
        
        # Brasil
        "sao paulo": "são paulo",
        "atletico mineiro": "atlético mineiro",
        "atletico paranaense": "athletico paranaense",
    }
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normaliza nome do time para matching"""
        name = name.lower().strip()
        
        # Remove palavras comuns
        remove_words = ['fc', 'cf', 'sc', 'afc', 'bfc', 'united', 'city']
        for word in remove_words:
            name = name.replace(f' {word}', '').replace(f'{word} ', '')
        
        # Remove caracteres especiais
        name = name.replace('.', '').replace('-', ' ')
        
        # Remove espaços extras
        name = ' '.join(name.split())
        
        return name
    
    @staticmethod
    def similarity_score(name1: str, name2: str) -> float:
        """Calcula score de similaridade entre dois nomes (0-1)"""
        # Normaliza ambos
        norm1 = TeamMatcher.normalize_name(name1)
        norm2 = TeamMatcher.normalize_name(name2)
        
        # Checa mapeamento manual primeiro
        if norm1 in TeamMatcher.KNOWN_MAPPINGS:
            norm1 = TeamMatcher.KNOWN_MAPPINGS[norm1]
        if norm2 in TeamMatcher.KNOWN_MAPPINGS:
            norm2 = TeamMatcher.KNOWN_MAPPINGS[norm2]
        
        # Se forem iguais após normalização, match perfeito
        if norm1 == norm2:
            return 1.0
        
        # Usa SequenceMatcher para calcular similaridade
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    @staticmethod
    def parse_datetime(dt_str: str) -> Optional[datetime]:
        """Parse datetime de diferentes formatos das APIs"""
        if not dt_str:
            return None
        
        # Formatos comuns das APIs
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",           # ISO 8601 UTC
            "%Y-%m-%dT%H:%M:%S",            # ISO sem Z
            "%Y-%m-%d %H:%M:%S",            # Simples
            "%Y-%m-%dT%H:%M:%S.%fZ",        # Com microsegundos
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except:
                continue
        
        return None
    
    @staticmethod
    def time_match(time1: str, time2: str, tolerance_hours: int = 3) -> bool:
        """
        Verifica se dois horários são próximos (±tolerance_hours)
        
        Args:
            time1: Timestamp do primeiro jogo
            time2: Timestamp do segundo jogo
            tolerance_hours: Tolerância em horas (padrão: 3h)
        
        Returns:
            True se os horários estão dentro da tolerância
        """
        dt1 = TeamMatcher.parse_datetime(time1)
        dt2 = TeamMatcher.parse_datetime(time2)
        
        # Se não conseguiu parsear algum, aceita (fallback ao comportamento antigo)
        if not dt1 or not dt2:
            return True
        
        # Calcula diferença absoluta
        diff = abs((dt1 - dt2).total_seconds() / 3600)  # Em horas
        
        return diff <= tolerance_hours
    
    @staticmethod
    def find_best_match(team_name: str, candidates: List[Dict], threshold: float = 0.7) -> Optional[Dict]:
        """
        Encontra o melhor match para um time em uma lista de candidatos
        
        Args:
            team_name: Nome do time para buscar
            candidates: Lista de dicts com 'name' e outros dados do time
            threshold: Score mínimo para considerar um match (0-1)
        
        Returns:
            Dict com dados do time matched, ou None se não houver match bom
        """
        best_score = 0.0
        best_match = None
        
        for candidate in candidates:
            candidate_name = candidate.get('name', '')
            score = TeamMatcher.similarity_score(team_name, candidate_name)
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Só retorna se passou do threshold
        if best_score >= threshold:
            return best_match
        
        return None
    
    @staticmethod
    def match_teams(odds_home: str, odds_away: str, 
                   api_football_matches: List[Dict], 
                   odds_datetime: str = None,
                   threshold: float = 0.7,
                   time_tolerance_hours: int = 3) -> Optional[Dict]:
        """
        Tenta fazer match de um jogo da The Odds API com um jogo da API-Football
        
        Args:
            odds_home: Nome do time mandante (The Odds API)
            odds_away: Nome do time visitante (The Odds API)
            api_football_matches: Lista de jogos da API-Football
            odds_datetime: Horário do jogo (The Odds API) - NOVO
            threshold: Score mínimo para considerar um match
            time_tolerance_hours: Tolerância de horário em horas (padrão: 3h)
        
        Returns:
            Dict com dados do jogo da API-Football, ou None se não houver match
        """
        for match in api_football_matches:
            home_name = match.get('home_team', '')
            away_name = match.get('away_team', '')
            match_datetime = match.get('date', '')
            
            # Calcula score para ambos os times
            home_score = TeamMatcher.similarity_score(odds_home, home_name)
            away_score = TeamMatcher.similarity_score(odds_away, away_name)
            
            # Verifica se os nomes batem
            if home_score >= threshold and away_score >= threshold:
                # NOVO: Verifica também o horário
                if odds_datetime and not TeamMatcher.time_match(odds_datetime, match_datetime, time_tolerance_hours):
                    print(f"   ⏰ Horários diferentes: {odds_datetime} vs {match_datetime} - descartando")
                    continue
                
                # Score combinado (média)
                combined_score = (home_score + away_score) / 2
                
                return {
                    **match,
                    'match_score': combined_score,
                    'home_match_score': home_score,
                    'away_match_score': away_score
                }
        
        return None
