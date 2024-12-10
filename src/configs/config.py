import logging
import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

class Config:
    CA_FILE = os.getenv('TLS_CA_FILE')
    ACCESS_TOKEN_SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY')
    REFRESH_TOKEN_SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))
    MONGODB_URI = os.getenv('MONGODB_URI', "mongodb://localhost:27017")
    IS_MONGO_LOCAL = os.getenv('IS_MONGO_LOCAL', 1)
    IS_STORAGE_LOCAL = os.getenv('IS_STORAGE_LOCAL', 1)
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', "admin@example.com")
    QUEST_EMAIL = os.getenv('QUEST_EMAIL', "quest@example.com")
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', "adminpass")
    QUEST_PASSWORD = os.getenv('QUEST_PASSWORD', "questpass")
    PORT = int(os.getenv('PORT', '8081'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def get_log_level(cls):
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(cls.LOG_LEVEL.upper(), logging.INFO)
