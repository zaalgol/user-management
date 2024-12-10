from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import uvicorn


from motor.motor_asyncio import AsyncIOMotorClient
from src.configs.config import Config
from src.services.init_service import InitService
from src.router.api import router
from src.logger_setup import setup_logger

logger = setup_logger(__name__)

def create_app():
    app = FastAPI()
    app.state.config = Config

    # Initialize MongoDB async client and set it in app state
    logger.info("Initializing MongoDB client.")
    MONGODB_URI = Config.MONGODB_URI
    if int(Config.IS_MONGO_LOCAL):
        mongo_client = AsyncIOMotorClient(MONGODB_URI)
    else:
        mongo_client = AsyncIOMotorClient(
            MONGODB_URI,
            tls=True,
            retryWrites=False,
            tlsCAFile=Config.CA_FILE,
            socketTimeoutMS=60000,
            connectTimeoutMS=60000
        )
    app.state.db = mongo_client['user-management-db']

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
