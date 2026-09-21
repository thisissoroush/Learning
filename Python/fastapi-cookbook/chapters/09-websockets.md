# Chapter 9 — WebSockets

> **Project:** `chat_platform`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter09)

---

## 🎯 What This Chapter Covers

WebSocket connections, authenticated WebSockets, multi-room chat, disconnect handling, broadcasting to multiple clients, and benchmarking WebSocket performance.

---

## 🔌 Basic WebSocket Endpoint

```python
from fastapi import FastAPI, WebSocket, WebSocketException, status
from fastapi.websockets import WebSocketDisconnect
import logging

app = FastAPI()
logger = logging.getLogger("uvicorn")

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()                          # must accept before sending
    await websocket.send_text("Welcome to the chat room!")

    try:
        while True:
            data = await websocket.receive_text()     # blocks until message arrives
            logger.info(f"Message received: {data}")

            if data == "disconnect":
                return await websocket.close(
                    code=status.WS_1000_NORMAL_CLOSURE,
                    reason="Disconnecting...",
                )

            if "bad message" in data:
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Inappropriate message",
                )

            await websocket.send_text("Message received!")

    except WebSocketDisconnect:
        logger.warning("Connection closed by the client")
```

**WebSocket lifecycle:**
```
Client → connect → server.accept()
                ↔ send/receive messages
Client → disconnect → WebSocketDisconnect raised
```

---

## 🔐 Secured WebSocket with Auth

```python
from typing import Annotated
from fastapi import WebSocket, Depends

def get_username_from_token(token: str) -> str:
    """Validate token and return username. Raise HTTPException if invalid."""
    user = decode_jwt_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user.username

@app.websocket("/secured-ws")
async def secured_websocket(
    websocket: WebSocket,
    username: Annotated[str, Depends(get_username_from_token)],
):
    await websocket.accept()
    await websocket.send_text(f"Welcome {username}!")

    async for data in websocket.iter_text():      # cleaner loop — auto-handles disconnect
        await websocket.send_text(f"You wrote: {data}")
```

**Passing auth to WebSocket:** Token in query param (`?token=...`) or first message — not headers (browsers don't support custom WS headers).

---

## 🏠 Multi-Room Chat with Connection Manager

```python
from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        # room_id -> list of connected WebSockets
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        self.active_connections[room_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, room_id: str, sender: WebSocket = None):
        for connection in self.active_connections[room_id]:
            if connection != sender:   # don't echo back to sender
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/chat/{room_id}")
async def chat_room(
    websocket: WebSocket,
    room_id: str,
    username: Annotated[str, Depends(get_username_from_token)],
):
    await manager.connect(websocket, room_id)
    await manager.broadcast(f"{username} joined the room", room_id)

    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(f"{username}: {message}", room_id, sender=websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(f"{username} left the room", room_id)
```

---

## 🔒 Exclusive Chatroom (Role-Based Access)

```python
@router.websocket("/exclusive-chat/{room_id}")
async def exclusive_chatroom(
    websocket: WebSocket,
    room_id: str,
    user: Annotated[UserWithRole, Depends(get_current_user)],
):
    if user.role != Role.premium:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Premium membership required",
        )
        return

    await manager.connect(websocket, room_id)
    # ... same chat logic
```

---

## 📊 Benchmarking WebSockets

```python
# benchmark_websocket.py
import asyncio
import websockets
import time

async def benchmark(n_messages: int = 1000):
    start = time.perf_counter()
    async with websockets.connect("ws://localhost:8000/ws") as ws:
        welcome = await ws.recv()
        for i in range(n_messages):
            await ws.send(f"message {i}")
            await ws.recv()
    elapsed = time.perf_counter() - start
    print(f"{n_messages} messages in {elapsed:.2f}s = {n_messages/elapsed:.0f} msg/s")

asyncio.run(benchmark(1000))
```

---

## 🔑 Key Takeaways

- Always `await websocket.accept()` before any `send_text()` / `receive_text()`
- `WebSocketDisconnect` is raised when the client closes — always catch it and clean up
- `WebSocketException(code, reason)` closes the connection with a specific WS status code
- `websocket.iter_text()` is a cleaner infinite loop than `while True: receive_text()`
- Auth in WebSockets: use query params for tokens (browsers can't set custom WS headers)
- `ConnectionManager` with a dict of room → connections is the standard broadcast pattern
- Close with `WS_1000_NORMAL_CLOSURE` for clean shutdown, `WS_1008_POLICY_VIOLATION` for policy violations
