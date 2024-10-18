from fastapi import WebSocket, WebSocketDisconnect
import os
import redis as Redis
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.redis = None

    async def connect(self, websocket: WebSocket, sensor_id: str):
        await websocket.accept()
        if sensor_id not in self.active_connections:
            self.active_connections[sensor_id] = []
        self.active_connections[sensor_id].append(websocket)

    def disconnect(self, websocket: WebSocket, sensor_id: str):
        self.active_connections[sensor_id].remove(websocket)
        if not self.active_connections[sensor_id]:
            del self.active_connections[sensor_id]

    async def broadcast(self, sensor_id: str, data: dict):
        if sensor_id in self.active_connections:
            connections = self.active_connections[sensor_id].copy()
            
            for connection in connections:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    print(f"Failed to send message to {sensor_id}: {e}")
                    self.disconnect(connection, sensor_id)

    async def start_redis_listener(self):
        self.redis = Redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            db=1
        )

        pubsub = self.redis.pubsub()
        pubsub.psubscribe('sensor_updates:*')


        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            
            if message:
                if message['type'] == 'pmessage':
                    sensor_id = message['channel'].decode().split(':')
                    sensor_id = ':'.join(sensor_id[1:])
                    message_data = message['data'].decode('utf-8')
                    try:
                        await self.broadcast(sensor_id, {"sensor_id": sensor_id, "data": message_data})
                    except Exception as e:
                        print(e)
            
            await asyncio.sleep(0.1)