# src/models/bet_history.py

from src.database.connection import get_db
from sqlalchemy import text
from datetime import datetime
from typing import List, Dict, Optional


class BetHistory:
    """Gerencia histórico de apostas usando PostgreSQL (via SQLAlchemy)."""

    def __init__(self):
        # Não precisa cursor aqui, porque usamos get_db() (SQLAlchemy session/connection)
        pass

    def add_bet(self, bet_data: Dict) -> str:
        """Adiciona nova aposta ao histórico"""
        bet_id = f"BET_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        with get_db() as db:
            query = text("""
                INSERT INTO bets (
                    bet_id, match, competition, market, odds, stake,
                    probability, ev, phase, status
                )
                VALUES (
                    :bet_id, :match, :competition, :market, :odds, :stake,
                    :probability, :ev, :phase, :status
                )
            """)

            db.execute(query, {
                "bet_id": bet_id,
                "match": bet_data["match"],
                "competition": bet_data.get("competition", ""),  # evita KeyError
                "market": bet_data["market"],
                "odds": bet_data["odds"],
                "stake": bet_data["stake"],
                "probability": bet_data.get("probability", 0.0),
                "ev": bet_data.get("ev", 0.0),
                "phase": bet_data.get("phase", 1),
                "status": "pending",
            })

        return bet_id

    def update_bet_result(self, bet_id: str, result: str) -> bool:
        """Atualiza resultado da aposta (won/lost/void)"""
        with get_db() as db:
            query = text("SELECT stake, odds FROM bets WHERE bet_id = :bet_id")
            bet = db.execute(query, {"bet_id": bet_id}).fetchone()

            if not bet:
                return False

            stake, odds = bet

            stake = float(stake)
            odds = float(odds)

            if result == "won":
                profit = round(stake * (odds - 1), 2)
            elif result == "lost":
                profit = -stake
            else:  # void
                profit = 0.0

            update_query = text("""
                UPDATE bets
                SET status = :status,
                    result = :result,
                    profit = :profit,
                    closed_at = NOW()
                WHERE bet_id = :bet_id
            """)

            db.execute(update_query, {
                "bet_id": bet_id,
                "status": result,
                "result": result,
                "profit": profit,
            })

        return True

    def get_pending_bets(self) -> List[Dict]:
        """Retorna apostas pendentes"""
        with get_db() as db:
            query = text("""
                SELECT *
                FROM bets
                WHERE status = 'pending'
                ORDER BY "timestamp" DESC
            """)
            rows = db.execute(query).fetchall()
            return [dict(row._mapping) for row in rows]

    def get_statistics(self, phase: Optional[int] = None) -> Dict:
        """Calcula estatísticas do histórico"""
        with get_db() as db:
            if phase is not None:
                query = text("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won,
                        SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as lost,
                        SUM(CASE WHEN status = 'void' THEN 1 ELSE 0 END) as void,
                        SUM(stake) as total_staked,
                        SUM(profit) as total_profit,
                        AVG(odds) as avg_odds,
                        AVG(stake) as avg_stake
                    FROM bets
                    WHERE phase = :phase AND status != 'pending'
                """)
                result = db.execute(query, {"phase": phase}).fetchone()
            else:
                query = text("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won,
                        SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as lost,
                        SUM(CASE WHEN status = 'void' THEN 1 ELSE 0 END) as void,
                        SUM(stake) as total_staked,
                        SUM(profit) as total_profit,
                        AVG(odds) as avg_odds,
                        AVG(stake) as avg_stake
                    FROM bets
                    WHERE status != 'pending'
                """)
                result = db.execute(query).fetchone()

            total = int(result.total or 0) if result else 0
            if total == 0:
                return {
                    "total_bets": 0,
                    "won": 0,
                    "lost": 0,
                    "void": 0,
                    "win_rate": 0,
                    "total_staked": 0,
                    "total_profit": 0,
                    "roi": 0,
                    "avg_odds": 0,
                    "avg_stake": 0,
                }

            won = int(result.won or 0)
            lost = int(result.lost or 0)
            void = int(result.void or 0)
            total_staked = float(result.total_staked or 0)
            total_profit = float(result.total_profit or 0)

            return {
                "total_bets": total,
                "won": won,
                "lost": lost,
                "void": void,
                "win_rate": round((won / total) * 100, 2) if total > 0 else 0,
                "total_staked": round(total_staked, 2),
                "total_profit": round(total_profit, 2),
                "roi": round((total_profit / total_staked) * 100, 2) if total_staked > 0 else 0,
                "avg_odds": round(float(result.avg_odds or 0), 2),
                "avg_stake": round(float(result.avg_stake or 0), 2),
            }

    def get_recent_bets(self, n: int = 10) -> List[Dict]:
        """Retorna as últimas N apostas"""
        with get_db() as db:
            query = text("""
                SELECT
                    bet_id,
                    match,
                    market,
                    odds,
                    stake,
                    status,
                    phase,
                    "timestamp",
                    CASE
                        WHEN status = 'won' THEN (odds * stake) - stake
                        WHEN status = 'lost' THEN -stake
                        WHEN status = 'void' THEN 0
                        ELSE NULL
                    END as result
                FROM bets
                ORDER BY "timestamp" DESC
                LIMIT :limit
            """)

            rows = db.execute(query, {"limit": n}).fetchall()
            return [dict(row._mapping) for row in rows]
