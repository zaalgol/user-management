from src.services.user_service import UserService
from src.configs.config import Config
from src.logger_setup import setup_logger

logger = setup_logger(__name__)

class InitService:
    def __init__(self, app):
        self.app = app
        self.db = app.state.db
        self.user_service = UserService(self.db)
    
    async def seed_admin_user(self):
        email = Config.ADMIN_EMAIL  
        password = Config.ADMIN_PASSWORD
        existing_user = await self.user_service.user_repository.get_user_by_email(email)
        if existing_user:
            logger.info(f"Admin user {email} already exists.")
            return existing_user
        else:
            logger.info(f"Creating admin user {email}.")
            return await self.user_service.create_user(email, password)
    
    async def seed_quest_user(self):
        email = Config.QUEST_EMAIL
        password = Config.QUEST_PASSWORD
        existing_user = await self.user_service.user_repository.get_user_by_email(email)
        if existing_user:
            logger.info(f"Quest user {email} already exists.")
            return existing_user
        else:
            logger.info(f"Creating quest user {email}.")
            return await self.user_service.create_user(email, password)
