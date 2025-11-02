import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.params import Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket

from app.core.app_status import AppStatus
from app.core.setting import settings
from app.initialize.database import lifespan
from app.initialize.websocket import socket_manage
from app.modules.user.controller import auth_router, user_router
from app.modules.user.dependencies import get_token_service
from app.modules.auth.security import TokenService
from app.utils.response import make_error_response


class Application:
    def __init__(self):
        self.app = FastAPI(lifespan=lifespan)
        self.manager = socket_manage
        self.setup_router()
        self.init_cors()
        self.configure_logging()
        # self.setup_websocket_router()

    def setup_router(self):
        """Define application routes here."""

        self.app.include_router(auth_router, prefix="/api/user", tags=["user"])
        self.app.include_router(user_router, prefix="/api/user", tags=["user"])

    def setup_websocket_router(self):
        """Define WebSocket routes here."""

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket,
                                     token_service: TokenService = Depends(get_token_service)):
            access_token = websocket.cookies.get("access_token", None)
            token_data = token_service.validate_token(access_token)
            if not token_data:
                await websocket.close()
                return
            user_id = token_data.get('sub', '')
            await self.manager.connect(websocket, user_id)
            try:
                while True:
                    await websocket.receive_json()
            except Exception:
                self.manager.disconnect(websocket)

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
