import time
from typing import Dict
from app.core.config import settings

try:
    from telegram import Bot
except Exception:
    Bot = None

class TelegramNotifier:
    def __init__(self):
        self.cooldowns: Dict[str, float] = {}
        self.bot = Bot(token=settings.telegram_bot_token) if Bot and settings.telegram_bot_token else None

    async def send_opportunity(self, key: str, text: str):
        if not self.bot or not settings.telegram_chat_id:
            return False
        now = time.time()
        if now - self.cooldowns.get(key, 0) < settings.notify_cooldown_seconds:
            return False
        await self.bot.send_message(chat_id=settings.telegram_chat_id, text=text)
        self.cooldowns[key] = now
        return True

notifier = TelegramNotifier()
