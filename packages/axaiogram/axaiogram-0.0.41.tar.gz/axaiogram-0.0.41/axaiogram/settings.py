from pydantic import BaseSettings


class BotSettings(BaseSettings):
    BOT_TOKEN: str

