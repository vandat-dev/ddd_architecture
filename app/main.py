import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.setting import settings
from app.initialize.database import lifespan
from app.initialize.websocket import socket_manage
from app.modules.user.presentation.rest.api import auth_router, user_router

from app.modules.user.presentation.websocket.endpoint import router as websocket_router

class Application:
    def __init__(self):
        self.app = FastAPI(lifespan=lifespan)
        self.manager = socket_manage
        self.setup_router()
        self.init_cors()
        self.configure_logging()

    def setup_router(self):
        """Define application routes here."""

        self.app.include_router(auth_router, prefix="/api/user", tags=["user"])
        self.app.include_router(user_router, prefix="/api/user", tags=["user"])
        self.app.include_router(websocket_router, tags=["websocket"])

    def init_cors(self):
        """Set up CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOW_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @staticmethod
    def configure_logging():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s : %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def start_app(self, host="0.0.0.0", port=8000):
        """Start the Uvicorn server."""
        uvicorn.run(self.app, host=host, port=port)


app_instance = Application()
app = app_instance.app

if __name__ == "__main__":
    # Run the application
    app_instance = Application()
    app_instance.start_app()
