import os
import time
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional

# Se você já tem esses módulos, beleza.
# Se não tiver Redis rodando, o código continua funcionando sem cache.
try:
    from src.cache.redis_client import RedisCache
except Exception:
    RedisCache = None


class TennisAPI:
    """
    RapidAPI - Ultimate Tennis
    - Base: https://ultimate-tennis1.p.rapidapi.com
    - Host: ultimate-tennis1.p.rapidapi.com

    IMPORTANTE:
    Alguns endpoints do menu NÃO batem 1:1 com os paths.
    Sempre copie o PATH exato do "Code Snippets" no RapidAPI.
    """

    def __init__(self):
        from config.config import Config

        self.api_key = Config.RAPIDAPI_TENNIS_KEY
        self.base_url = getattr(Config, "RAPIDAPI_TENNIS_BASE", "https://ultimate-tennis1.p.rapidapi.com").rstrip("/")
        self.host = "ultimate-tennis1.p.rapidapi.com"

        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.host,
        }

        # Cache (opcional)
        self.cache = RedisCache() if RedisCache else None

        # Endpoints (defaults). Se der 404, COPIE do Code Snippets e ajuste via .env/Config.
        # Ex.: RAPIDAPI_TENNIS_EP_ATP_RANKINGS="/atp/official_players_rankings" (exemplo)
        self.EP_LIVE_SCORES = os.getenv("RAPIDAPI_TENNIS_EP_LIVE_SCORES", "/live_scores")
        self.EP_MATCH_DETAILS = os.getenv("RAPIDAPI_TENNIS_EP_MATCH_DETAILS", "/match_details/{match_id}")
        self.EP_ATP_DAILY_SCHEDULE = os.getenv("RAPIDAPI_TENNIS_EP_ATP_DAILY_SCHEDULE", "/atp/tournament_daily_schedule/{tournament_id}")
        self.EP_ATP_RANKINGS = os.getenv("RAPIDAPI_TENNIS_EP_ATP_RANKINGS", "/atp/official_atp_players_rankings")
        self.EP_WTA_RANKINGS = os.getenv("RAPIDAPI_TENNIS_EP_WTA_RANKINGS", "/wta/official_wta_players_rankings")

        # Plano free é MUITO baixo (60/mês). Cache ajuda muito.
        self.default_timeout = 20

    # -------------------------
    # Core request
    # -------------------------
    def _cache_get(self, key: str) -> Optional[Any]:
        if not self.cache:
            return None
        try:
            return self.cache.get(key)
        except Exception:
            return None

    def _cache_set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if not self.cache:
            return
        try:
            self.cache.set(key, value, ttl_seconds)
        except Exception:
            pass

    def _get_json(self, path: str, params: Optional[Dict[str, Any]] = None, cache_key: Optional[str] = None, cache_ttl: int = 120) -> Dict[str, Any]:
        if cache_key:
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

        url = f"{self.base_url}{path}"

        # retry simples pra 429
        for attempt in range(3):
            resp = requests.get(url, headers=self.headers, params=params or {}, timeout=self.default_timeout)

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", "0") or 0) or (2 ** attempt)
                time.sleep(wait)
                continue

            # Se 404, devolve texto pra você ajustar o path
            if resp.status_code == 404:
                raise RuntimeError(f"404 Not Found em {url}. Corpo: {resp.text}")

            # Se 403, normalmente é auth/subscription, mas já resolvemos com key nova.
            if resp.status_code == 403:
                raise RuntimeError(f"403 Forbidden em {url}. Corpo: {resp.text}")

            resp.raise_for_status()

            data = resp.json() if resp.text else {}

            # Alguns endpoints retornam 200 com "internal_error"
            if isinstance(data, dict) and "internal_error" in data:
                # não é erro de rede/auth, só sem jogos/sem dados naquele momento
                return data

            if cache_key:
                self._cache_set(cache_key, data, cache_ttl)

            return data

        raise RuntimeError("Falhou após retries (provável 429 contínuo)")

    # -------------------------
    # Métodos públicos
    # -------------------------
    def get_live_scores(self) -> List[Dict[str, Any]]:
        """
        Endpoint que você já testou que funciona: /live_scores
        Retorno costuma vir como {"matches": [...]}
        """
        cache_key = f"tennis:live_scores:{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
        data = self._get_json(self.EP_LIVE_SCORES, cache_key=cache_key, cache_ttl=60)

        if isinstance(data, dict) and "internal_error" in data:
            return []

        return data.get("matches", []) if isinstance(data, dict) else []

    def get_live_matches(self) -> List[Dict[str, Any]]:
        """
        No seu menu tem "Live Matches Stats", mas o path que você usou estava errado.
        Enquanto você não confirmar o path correto no Code Snippets, usamos live_scores.
        """
        return self.get_live_scores()

    def get_match_details(self, match_id: int) -> Dict[str, Any]:
        path = self.EP_MATCH_DETAILS.format(match_id=match_id)
        cache_key = f"tennis:match_details:{match_id}"
        return self._get_json(path, cache_key=cache_key, cache_ttl=300)

    def get_atp_daily_schedule(self, tournament_id: int) -> List[Dict[str, Any]]:
        path = self.EP_ATP_DAILY_SCHEDULE.format(tournament_id=tournament_id)
        cache_key = f"tennis:atp:schedule:{tournament_id}:{datetime.now().strftime('%Y-%m-%d')}"
        data = self._get_json(path, cache_key=cache_key, cache_ttl=300)
        return data.get("matches", []) if isinstance(data, dict) else []

    def get_atp_rankings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        ATP rankings (singles/current).
        Endpoint (confirmado): /rankings/atp/singles/50/current

        OBS: O payload do ATP vem com chaves diferentes do WTA:
        - Name, Points, Rank, id, Next best
        """
        cache_key = "tennis:atp:rankings"
        data = self._get_json(self.EP_ATP_RANKINGS, cache_key=cache_key, cache_ttl=6 * 3600)

        items = data.get("data", []) if isinstance(data, dict) else []
        normalized = [{
            "player_id": it.get("id"),                 # ex: "s0ag"
            "player_name": it.get("Name"),             # ex: "J. Sinner"
            "rank": it.get("Rank"),                    # pode vir "-" nesse endpoint
            "points": it.get("Points"),                # pode vir null nesse endpoint
            "country": it.get("country"),              # geralmente não vem no ATP aqui
            "movement": it.get("movement"),            # geralmente não vem no ATP aqui
            "ranked_at": it.get("rankedAt"),           # geralmente não vem no ATP aqui
            "tournaments_played": it.get("tournamentsPlayed"),  # geralmente não vem no ATP aqui
            "next_best": it.get("Next best"),
        } for it in items]

        return normalized[:limit]

    def get_wta_rankings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        WTA rankings (singles/current).
        Path real (confirmado): /rankings/wta/singles/50/current
        """
        cache_key = "tennis:wta:rankings"
        data = self._get_json(self.EP_WTA_RANKINGS, cache_key=cache_key, cache_ttl=6 * 3600)

        items = data.get("data", []) if isinstance(data, dict) else []
        normalized = [{
            "player_id": it.get("ID"),
            "player_name": it.get("name"),
            "rank": it.get("ranking"),
            "points": it.get("points"),
            "country": it.get("country"),
            "movement": it.get("movement"),
            "ranked_at": it.get("rankedAt"),
            "tournaments_played": it.get("tournamentsPlayed"),
        } for it in items]

        return normalized[:limit]
