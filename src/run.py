from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pymongo import MongoClient
import uvicorn
import asyncio

from src.configs.config import Config
from src.services.init_service import InitService
from src.router.api import router
from src.logger_setup import setup_logger

logger = setup_logger(__name__)

def generate_mongo_client():
    MONGODB_URI = Config.MONGODB_URI
    try:
        if int(Config.IS_MONGO_LOCAL):
            mongo_client = MongoClient(MONGODB_URI)
        else:
            mongo_client = MongoClient(
                MONGODB_URI,
                tls=True,
                retryWrites=False,
                tlsCAFile=Config.CA_FILE,
                socketTimeoutMS=60000,
                connectTimeoutMS=60000
            )
        db = mongo_client['user-management-db']
        return db
    except Exception as e:
        logger.error(f"Failed to create MongoDB client: {e}")
        raise

def create_app():
    app = FastAPI()
    app.state.config = Config

    # Initialize MongoDB client and set it in app state
    logger.info("Initializing MongoDB client.")
    app.state.db = generate_mongo_client()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    logger.info("Including main router.")
    app.include_router(router)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Seeding initial data.")
        init_service = InitService(app)
        await init_service.seed_admin_user()
        await init_service.seed_quest_user()

    return app

app = create_app()

if __name__ == '__main__':
    logger.info("Starting Uvicorn server.")
    uvicorn.run(app, host='0.0.0.0', port=Config.PORT)
