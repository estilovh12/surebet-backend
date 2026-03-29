from pydantic import BaseModel, Field
from typing import List, Optional

class Outcome(BaseModel):
    name: str
    price: float
    point: Optional[float] = None

class BookmakerMarket(BaseModel):
    bookmaker: str
    market_key: str
    outcomes: List[Outcome]
    last_update: Optional[str] = None
    deep_link: Optional[str] = None

class EventOdds(BaseModel):
    event_id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: Optional[str] = None
    markets: List[BookmakerMarket] = Field(default_factory=list)

class BetLeg(BaseModel):
    bookmaker: str
    selection: str
    odd: float
    point: Optional[float] = None
    deep_link: Optional[str] = None

class ArbOpportunity(BaseModel):
    event_id: str
    event_name: str
    sport_key: str
    market_key: str
    arb_percent: float
    profit_percent: float
    legs: List[BetLeg]
    recommended_stakes: List[float]
    guaranteed_payout: float
    guaranteed_profit: float
    score: float
    commence_time: Optional[str] = None
