from __future__ import annotations

import json
import asyncio
from typing import Dict, List, Optional, Any
from fastapi import WebSocket
from ..core.config import get_settings

class ConnectionManager:
    def __init__(self):
        # Maps user_id to their WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        # Maps role to list of user_ids for that role
        self.role_groups: Dict[str, List[str]] = {}
        self._redis = None
        self._pubsub = None
        self._redis_task = None
        self._ping_task = None
        self._channel_name = "ws_messages"

    def start_heartbeat(self):
        self._ping_task = asyncio.create_task(self._ping_clients_periodically())

    async def _ping_clients_periodically(self):
        while True:
            await asyncio.sleep(45) # Send ping every 45 secs
            disconnected_users = []
            for user_id, connection in self.active_connections.items():
                try:
                    await connection.send_text(json.dumps({"type": "ping"}))
                except Exception:
                    disconnected_users.append(user_id)
            
            for user_id in disconnected_users:
                self.disconnect(user_id)

    async def init_redis(self):
        settings = get_settings()
        if not settings.redis_url:
            return

        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)
            self._pubsub = self._redis.pubsub()
            await self._pubsub.subscribe(self._channel_name)
            self._redis_task = asyncio.create_task(self._listen_to_redis())
            print(f"Connected to Redis for WebSocket Pub/Sub: {settings.redis_url}")
        except Exception as e:
            print(f"Failed to connect to Redis for WebSocket: {e}")
            self._redis = None
            self._pubsub = None

    async def _listen_to_redis(self):
        try:
            async for message in self._pubsub.listen():
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    target_type = data.get("target_type")
                    target_id = data.get("target_id")
                    payload = data.get("payload")

                    if target_type == "personal":
                        await self._send_local_personal(payload, target_id)
                    elif target_type == "role":
                        await self._send_local_role(payload, target_id)
                    elif target_type == "broadcast":
                        await self._send_local_broadcast(payload)
        except Exception as e:
            print(f"Redis listener error: {e}")

    async def connect(self, websocket: WebSocket, user_id: str, role: Optional[str] = None):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        if role:
            if role not in self.role_groups:
                self.role_groups[role] = []
            if user_id not in self.role_groups[role]:
                self.role_groups[role].append(user_id)

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # Clean up from role groups
        for role in list(self.role_groups.keys()):
            if user_id in self.role_groups[role]:
                self.role_groups[role].remove(user_id)
            if not self.role_groups[role]:
                del self.role_groups[role]

    async def send_personal_message(self, message: dict, user_id: str):
        if self._redis:
            await self._redis.publish(self._channel_name, json.dumps({
                "target_type": "personal",
                "target_id": user_id,
                "payload": message
            }))
        else:
            await self._send_local_personal(message, user_id)

    async def _send_local_personal(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        if self._redis:
            await self._redis.publish(self._channel_name, json.dumps({
                "target_type": "broadcast",
                "target_id": None,
                "payload": message
            }))
        else:
            await self._send_local_broadcast(message)

    async def _send_local_broadcast(self, message: dict):
        disconnected_users = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                disconnected_users.append(user_id)
        
        for user_id in disconnected_users:
            self.disconnect(user_id)

    async def broadcast_to_role(self, message: dict, role: str):
        if self._redis:
            await self._redis.publish(self._channel_name, json.dumps({
                "target_type": "role",
                "target_id": role,
                "payload": message
            }))
        else:
            await self._send_local_role(message, role)

    async def _send_local_role(self, message: dict, role: str):
        if role in self.role_groups:
            for user_id in list(self.role_groups[role]):
                await self._send_local_personal(message, user_id)
