from typing import List
import httpx
from app.core.config import settings
from app.models.schemas import EventOdds, BookmakerMarket, Outcome
from app.providers.base import Provider

class TheOddsAPIProvider(Provider):
    name = "theoddsapi"

    async def fetch_events(self, sport_key: str) -> List[EventOdds]:
        if not settings.api_key_the_odds:
            return []
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
        params = {
            "apiKey": settings.api_key_the_odds,
            "regions": ",".join(settings.regions_list),
            "markets": ",".join(settings.markets_list),
            "oddsFormat": "decimal",
            "dateFormat": "iso",
            "includeLinks": "true",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        events: List[EventOdds] = []
        for e in data:
            event = EventOdds(
                event_id=e["id"],
                sport_key=e["sport_key"],
                home_team=e.get("home_team", "Home"),
                away_team=e.get("away_team", "Away"),
                commence_time=e.get("commence_time"),
                markets=[],
            )
            for bm in e.get("bookmakers", []):
                for market in bm.get("markets", []):
                    event.markets.append(
                        BookmakerMarket(
                            bookmaker=bm.get("title", "Unknown"),
                            market_key=market.get("key", "unknown"),
                            outcomes=[Outcome(name=o["name"], price=float(o["price"]), point=o.get("point")) for o in market.get("outcomes", [])],
                            last_update=bm.get("last_update"),
                            deep_link=(bm.get("links") or {}).get("event"),
                        )
                    )
            events.append(event)
        return events
