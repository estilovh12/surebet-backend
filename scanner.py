import asyncio
from datetime import datetime, timezone
from app.core.config import settings
from app.providers.the_odds_api import TheOddsAPIProvider
from app.providers.mock_provider import MockProvider
from app.services.arb import build_arbs_for_event
from app.services.notifier import notifier
from app.storage.runtime import store

providers = [MockProvider(), TheOddsAPIProvider()]

async def scan_once():
    ops = []
    for sport in settings.sports_list:
        merged_events = []
        for provider in providers:
            try:
                merged_events.extend(await provider.fetch_events(sport))
            except Exception:
                continue
        for event in merged_events:
            ops.extend(build_arbs_for_event(event, min_profit_percent=settings.min_profit_percent))

    ops = [o for o in ops if o.arb_percent <= settings.max_arb_percent]
    ops = sorted(ops, key=lambda x: (x.score, x.profit_percent), reverse=True)[:300]
    store.opportunities = ops
    store.last_scan = datetime.now(timezone.utc).isoformat()
    store.history.append({
        "ts": store.last_scan,
        "count": len(ops),
        "best_profit": round(max([o.profit_percent for o in ops], default=0.0), 2),
        "avg_profit": round(sum([o.profit_percent for o in ops]) / len(ops), 2) if ops else 0.0,
    })

    for op in ops[:10]:
        key = f"{op.event_id}-{op.market_key}-{op.profit_percent}"
        msg = f"Surebet {op.event_name}\nMercado: {op.market_key}\nLucro: {op.profit_percent}%\nArb: {op.arb_percent}%"
        await notifier.send_opportunity(key, msg)

async def scanner_loop():
    while True:
        await scan_once()
        await asyncio.sleep(settings.scan_interval_seconds)
