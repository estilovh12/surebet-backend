from collections import deque
from typing import Deque, List
from app.models.schemas import ArbOpportunity

class RuntimeStore:
    def __init__(self):
        self.opportunities: List[ArbOpportunity] = []
        self.last_scan = None
        self.history: Deque[dict] = deque(maxlen=120)

store = RuntimeStore()
