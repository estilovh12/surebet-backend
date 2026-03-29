from typing import List
from app.models.schemas import EventOdds, BookmakerMarket, Outcome
from app.providers.base import Provider

class MockProvider(Provider):
    name = "mock"

    async def fetch_events(self, sport_key: str) -> List[EventOdds]:
        return [
            EventOdds(
                event_id=f"mock-{sport_key}-1",
                sport_key=sport_key,
                home_team="Palmeiras",
                away_team="Flamengo",
                commence_time="2026-03-30T21:00:00Z",
                markets=[
                    BookmakerMarket(bookmaker="Book A", market_key="h2h", outcomes=[
                        Outcome(name="Palmeiras", price=2.28), Outcome(name="Draw", price=3.55), Outcome(name="Flamengo", price=3.8)
                    ], deep_link="https://example.com/a"),
                    BookmakerMarket(bookmaker="Book B", market_key="h2h", outcomes=[
                        Outcome(name="Palmeiras", price=2.6), Outcome(name="Draw", price=3.2), Outcome(name="Flamengo", price=3.0)
                    ], deep_link="https://example.com/b"),
                    BookmakerMarket(bookmaker="Book C", market_key="h2h", outcomes=[
                        Outcome(name="Palmeiras", price=2.35), Outcome(name="Draw", price=3.7), Outcome(name="Flamengo", price=3.4)
                    ], deep_link="https://example.com/c"),
                    BookmakerMarket(bookmaker="Book A", market_key="totals", outcomes=[
                        Outcome(name="Over", price=2.12, point=2.5), Outcome(name="Under", price=2.05, point=2.5)
                    ]),
                    BookmakerMarket(bookmaker="Book C", market_key="totals", outcomes=[
                        Outcome(name="Over", price=1.98, point=2.5), Outcome(name="Under", price=2.15, point=2.5)
                    ]),
                ],
            )
        ]
