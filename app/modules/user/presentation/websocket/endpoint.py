import logging
from fastapi import APIRouter, WebSocket, Depends
from app.initialize.websocket import socket_manage
from app.modules.auth.security import TokenService
from app.modules.user.dependencies import get_token_service

router = APIRouter()
manager = socket_manage

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             token_service: TokenService = Depends(get_token_service)):
    access_token = websocket.cookies.get("access_token", None)
    token_data = token_service.validate_token(access_token)
    if not token_data:
        await websocket.close()
        return
    user_id = token_data.get('sub', '')
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_json()
    except Exception as e:
        logging.info(f"WebSocket disconnected: {e}")
        manager.disconnect(websocket)
