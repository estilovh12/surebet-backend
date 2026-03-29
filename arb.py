from collections import defaultdict
from itertools import product
from typing import Dict, List, Tuple
from app.models.schemas import ArbOpportunity, BetLeg, EventOdds


def _normalize_outcome_key(market_key: str, outcome_name: str, point):
    if market_key in {"totals", "spreads"}:
        return f"{outcome_name}|{point}"
    return outcome_name


def split_stakes(total_stake: float, odds: List[float]) -> Tuple[List[float], float, float]:
    inv_sum = sum(1 / o for o in odds)
    stakes = [(total_stake * (1 / o) / inv_sum) for o in odds]
    payout = min(s * o for s, o in zip(stakes, odds))
    profit = payout - total_stake
    return [round(s, 2) for s in stakes], round(payout, 2), round(profit, 2)


def _score_opportunity(profit_percent: float, bookmaker_count: int, avg_age_penalty: float) -> float:
    score = profit_percent * 15 + bookmaker_count * 5 - avg_age_penalty
    return round(max(score, 0), 2)


def build_arbs_for_event(event: EventOdds, min_profit_percent: float = 0.5, total_stake: float = 1000.0) -> List[ArbOpportunity]:
    grouped: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))

    for market in event.markets:
        for outcome in market.outcomes:
            key = _normalize_outcome_key(market.market_key, outcome.name, outcome.point)
            grouped[market.market_key][key].append((market.bookmaker, outcome.price, outcome.point, market.deep_link))

    opportunities: List[ArbOpportunity] = []

    for market_key, outcome_map in grouped.items():
        if market_key == "h2h":
            needed_keys = list(outcome_map.keys())
        elif market_key in {"totals", "spreads"}:
            # only compare exact mirrored point combinations available across books
            needed_keys = list(outcome_map.keys())
        else:
            needed_keys = list(outcome_map.keys())

        if len(needed_keys) < 2:
            continue

        candidate_lists = [sorted(outcome_map[k], key=lambda x: x[1], reverse=True)[:3] for k in needed_keys]

        for combo in product(*candidate_lists):
            books = [c[0] for c in combo]
            odds = [c[1] for c in combo]
            if len(set(books)) < 2:
                continue
            arb_percent = sum(1 / o for o in odds) * 100
            profit_percent = 100 - arb_percent
            if profit_percent < min_profit_percent:
                continue
            stakes, payout, profit = split_stakes(total_stake, odds)
            legs = [
                BetLeg(bookmaker=combo[i][0], selection=needed_keys[i], odd=combo[i][1], point=combo[i][2], deep_link=combo[i][3])
                for i in range(len(combo))
            ]
            score = _score_opportunity(profit_percent, len(set(books)), 0)
            opportunities.append(
                ArbOpportunity(
                    event_id=event.event_id,
                    event_name=f"{event.home_team} x {event.away_team}",
                    sport_key=event.sport_key,
                    market_key=market_key,
                    arb_percent=round(arb_percent, 2),
                    profit_percent=round(profit_percent, 2),
                    legs=legs,
                    recommended_stakes=stakes,
                    guaranteed_payout=payout,
                    guaranteed_profit=profit,
                    score=score,
                    commence_time=event.commence_time,
                )
            )

    unique = {}
    for op in opportunities:
        key = (op.event_id, op.market_key, tuple((l.bookmaker, l.selection, l.odd) for l in op.legs))
        unique[key] = op
    return sorted(unique.values(), key=lambda x: (x.profit_percent, x.score), reverse=True)
