from abc import ABC, abstractmethod
from typing import List
from app.models.schemas import EventOdds

class Provider(ABC):
    name: str

    @abstractmethod
    async def fetch_events(self, sport_key: str) -> List[EventOdds]:
        raise NotImplementedError
