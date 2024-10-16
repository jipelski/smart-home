from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import ConnectionManager
import asyncio

router = APIRouter()

manager = ConnectionManager()

@router.on_event("startup")
async def startup_event():
    asyncio.create_task(manager.start_redis_listener())

@router.websocket("/ws/sensor/{sensor_id}")
async def sensor_updates(websocket: WebSocket, sensor_id: str):
    await manager.connect(websocket, sensor_id)
    try:
        while True:
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket, sensor_id)