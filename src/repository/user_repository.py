from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.logger_setup import setup_logger

logger = setup_logger(__name__)

class UserRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    @property
    def db(self):
        return self._db

    @property
    def users_collection(self):
        return self.db['users']
    
    async def get_user_by_id(self, user_id):
        try:
            return await self.users_collection.find_one({"_id": ObjectId(user_id), "isDeleted": {"$ne": True}})
        except Exception as e:
            logger.error(f"Error fetching user by id {user_id}: {e}")
            return None

    async def get_user_by_email(self, email):
        try:
            return await self.users_collection.find_one({"email": email, "isDeleted": {"$ne": True}})
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            return None

    async def create_user(self, email, password):
        try:
            user_exists = await self.users_collection.find_one({"email": email})
            if user_exists:
                return None  # Indicate user already exists
            user = {
                "email": email,
                "password": password
            }
            result = await self.users_collection.insert_one(user)
            return {"_id": result.inserted_id, **user}
        except Exception as e:
            logger.error(f"Exception creating user {email}: {e}")
            return None

    async def update_password(self, user_id, new_password):
        try:
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id), "isDeleted": {"$ne": True}},
                {"$set": {"password": new_password}}
            )
            return result.modified_count == 1
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False
