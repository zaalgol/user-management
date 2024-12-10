from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pymongo import MongoClient
import uvicorn

from configs.config import Config
from services.init_service import InitService
from router.api import router
from logger_setup import setup_logger

logger = setup_logger(__name__)

def init_system(app: FastAPI):
    logger.info("Seeding initial data.")
    init_service = InitService(app)
    init_service.seed_admin_user()
    init_service.seed_quest_user()

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

    # Seed initial data
    init_system(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Could replaced by [your_frontend_domain]
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    logger.info("Including main router.")
    app.include_router(router)

    return app

app = create_app()

if __name__ == '__main__':
    logger.info("Starting Uvicorn server.")
    uvicorn.run(app, host='0.0.0.0', port=Config.PORT)
