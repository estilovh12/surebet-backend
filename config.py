from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    app_name: str = "Surebet Pro V2"
    debug: bool = True
    api_key_the_odds: str = ""
    api_key_oddsapiio: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    redis_url: str = "redis://redis:6379/0"
    database_url: str = "postgresql://postgres:postgres@postgres:5432/surebet"
    scan_interval_seconds: int = 15
    sports: str = "soccer_brazil_campeonato, soccer_epl, basketball_nba"
    regions: str = "eu,uk,us"
    markets: str = "h2h,totals,spreads"
    min_profit_percent: float = 0.5
    max_arb_percent: float = 99.4
    notify_cooldown_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def sports_list(self) -> List[str]:
        return [s.strip() for s in self.sports.split(",") if s.strip()]

    @property
    def markets_list(self) -> List[str]:
        return [m.strip() for m in self.markets.split(",") if m.strip()]

    @property
    def regions_list(self) -> List[str]:
        return [r.strip() for r in self.regions.split(",") if r.strip()]

settings = Settings()
