from pymongo.database import Database
from src.logger_setup import setup_logger
from fastapi.concurrency import run_in_threadpool

logger = setup_logger(__name__)

class TokenRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db: Database):
        self.collection = db['refresh_tokens']

    async def save_refresh_token(self, token_id, user_id, expires_at):
        await run_in_threadpool(
            self.collection.insert_one,
            {
                "_id": token_id,
                "user_id": user_id,
                "expires_at": expires_at
            }
        )

    async def delete_refresh_token(self, token_id):
        await run_in_threadpool(
            self.collection.delete_one,
            {"_id": token_id}
        )

    async def get_refresh_token(self, token_id):
        return await run_in_threadpool(
            self.collection.find_one,
            {"_id": token_id}
        )
