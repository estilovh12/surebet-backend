from collections import Counter
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.storage.runtime import store
import asyncio

router = APIRouter()


def _filtered(limit: int = 50, min_profit: float = 0.0, sport: str | None = None, market: str | None = None, q: str | None = None, sort: str = "score"):
    qn = (q or "").strip().lower()
    items = []
    for o in store.opportunities:
        if o.profit_percent < min_profit:
            continue
        if sport and o.sport_key != sport:
            continue
        if market and o.market_key != market:
            continue
        if qn:
            hay = " ".join([
                o.event_name,
                o.sport_key,
                o.market_key,
                *[l.bookmaker for l in o.legs],
                *[l.selection for l in o.legs],
            ]).lower()
            if qn not in hay:
                continue
        items.append(o)

    sorters = {
        "score": lambda x: (x.score, x.profit_percent, x.guaranteed_profit),
        "profit": lambda x: (x.profit_percent, x.score),
        "payout": lambda x: (x.guaranteed_payout, x.profit_percent),
        "time": lambda x: (x.commence_time or "", x.profit_percent),
    }
    items = sorted(items, key=sorters.get(sort, sorters["score"]), reverse=(sort != "time"))
    return items[:limit]


@router.get('/health')
async def health():
    return {"ok": True, "last_scan": store.last_scan, "count": len(store.opportunities), "history_points": len(store.history)}


@router.get('/opportunities')
async def opportunities(limit: int = 50, min_profit: float = 0.0, sport: str | None = None, market: str | None = None, q: str | None = None, sort: str = "score"):
    data = [o.model_dump() for o in _filtered(limit, min_profit, sport, market, q, sort)]
    return {"last_scan": store.last_scan, "items": data}


@router.get('/stats')
async def stats(min_profit: float = 0.0):
    items = [o for o in store.opportunities if o.profit_percent >= min_profit]
    sports = Counter(o.sport_key for o in items)
    markets = Counter(o.market_key for o in items)
    best = max(items, key=lambda x: x.profit_percent).model_dump() if items else None
    avg_profit = round(sum(o.profit_percent for o in items) / len(items), 2) if items else 0.0
    total_guaranteed = round(sum(o.guaranteed_profit for o in items), 2) if items else 0.0
    return {
        "last_scan": store.last_scan,
        "total": len(items),
        "avg_profit_percent": avg_profit,
        "best": best,
        "sports": sports,
        "markets": markets,
        "history": list(store.history),
        "total_guaranteed_profit_visible": total_guaranteed,
    }


@router.websocket('/ws/opportunities')
async def ws_opportunities(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({
                "last_scan": store.last_scan,
                "items": [o.model_dump() for o in store.opportunities[:50]],
                "history": list(store.history),
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return
