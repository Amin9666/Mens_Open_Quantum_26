import json
import re
from pathlib import Path

DEFAULT_RANK_SCORE = {
    None: 60,   # unseeded direct entry
    "Q": 90,    # qualifier — came through 3 extra rounds
    "W": 100,   # wild card — typically weakest field
    "L": 95,    # lucky loser
}

# transliteration/name-format exceptions the fuzzy matcher can't resolve on its own
NAME_OVERRIDES = {
    "aleksandr shevchenko": "alexander shevchenko",
}

_RANKINGS_PATH = Path(__file__).parent.parent / "data" / "atp_rankings.json"
_ATP_RANKS = None


def _normalize(name):
    n = name.lower()
    n = re.sub(r"[-.]", " ", n)
    n = re.sub(r"[^a-z ]", "", n)
    return re.sub(r"\s+", " ", n).strip()


def _load_atp_ranks():
    global _ATP_RANKS
    if _ATP_RANKS is None:
        if _RANKINGS_PATH.exists():
            raw = json.loads(_RANKINGS_PATH.read_text())["ranks"]
            _ATP_RANKS = {_normalize(k): v for k, v in raw.items()}
        else:
            _ATP_RANKS = {}
    return _ATP_RANKS


def atp_rank(name):
    """Look up a player's real ATP rank by name, or None if not found."""
    ranks = _load_atp_ranks()
    n = _normalize(name)
    n = NAME_OVERRIDES.get(n, n)
    if n in ranks:
        return ranks[n]
    parts = n.split()
    reversed_n = " ".join(parts[::-1])
    if reversed_n in ranks:
        return ranks[reversed_n]
    for k, v in ranks.items():
        if k.startswith(n) or n.startswith(k):
            return v
    return None


def seed_strength(seed, status, name=None):
    """Lower is stronger. Prefers the player's real current ATP rank; falls back to
    seed number, then to a status-based estimate (Q/W/L/unseeded) if neither is
    available."""
    if name is not None:
        rank = atp_rank(name)
        if rank is not None:
            return rank
    if seed is not None:
        return seed
    return DEFAULT_RANK_SCORE.get(status, DEFAULT_RANK_SCORE[None])


def parse_games(score_str):
    """Return (games_won, games_lost) for the match winner from a score string like
    '6-4 3-6 6-7(7) 7-5 6-4' or '7-6(4) 6-4 3-0 Ret.'"""
    sets = score_str.replace("Ret.", "").strip().split()
    won, lost = 0, 0
    for s in sets:
        s = re.sub(r"\(\d+\)", "", s)
        if "-" not in s:
            continue
        a, b = s.split("-")
        try:
            won += int(a)
            lost += int(b)
        except ValueError:
            continue
    return won, lost


def build_player_record(name, seed, status, score_str, sets_played, retirement=False):
    games_won, games_lost = parse_games(score_str)
    total_games = games_won + games_lost
    dominance = (games_won / total_games) if total_games else 0.5
    return {
        "name": name,
        "seed": seed,
        "status": status,
        "rank_score": seed_strength(seed, status, name=name),
        "sets_played": sets_played,
        "dominance": dominance,
        "retirement_win": retirement,
    }


def load_r1_winners(draw_json):
    """Return list of 64 winner records in bracket order, from parsed R1 match data."""
    winners = []
    for m in draw_json["matches"]:
        winner_key = m["winner"]
        loser_key = "p2" if winner_key == "p1" else "p1"
        w = m[winner_key]
        rec = build_player_record(
            name=w["name"],
            seed=w.get("seed"),
            status=w.get("status"),
            score_str=m["score"],
            sets_played=m["sets_played"],
            retirement=m.get("retirement", False),
        )
        winners.append(rec)
    return winners


def build_round_matchups(winners):
    """Pair up adjacent winners into next-round matchups, bracket-order."""
    return [(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]
