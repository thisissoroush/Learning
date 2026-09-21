# Chapter 9 — WebSockets

> **Project:** `chat_platform`

---

## 🎯 What This Chapter Covers

How WebSockets differ from HTTP, building a basic chat endpoint, handling disconnects and errors gracefully, adding authentication to WebSocket connections, building a multi-room broadcast system with a `ConnectionManager`, and benchmarking WebSocket throughput.

---

## 🧠 HTTP vs WebSockets — The Key Difference

```
HTTP (request/response):
  Client → sends request → Server → sends response → connection closes
  New message = new HTTP request
  Server CANNOT push to client without a request

WebSocket (full-duplex):
  Client → connects → Server acknowledges (handshake)
  ↕ Both sides can send messages at any time ↕
  Connection stays open until either side closes it
```

WebSockets are the right choice for:
- Real-time chat
- Live notifications
- Collaborative editing
- Live dashboards (prices, scores, metrics)
- Multiplayer game state

---

## 🔌 Basic WebSocket Endpoint — Step by Step

```python
from fastapi import FastAPI, WebSocket, WebSocketException, status
from fastapi.websockets import WebSocketDisconnect
import logging

app = FastAPI()
logger = logging.getLogger("uvicorn")

@app.websocket("/ws")
async def basic_websocket(websocket: WebSocket):
    """
    Basic WebSocket endpoint — echoes messages back.
    The lifecycle:
    1. Client connects (TCP + WebSocket handshake)
    2. We call accept() — must be first
    3. Loop: receive message, do something, send response
    4. Either side can close — WebSocketDisconnect is raised
    """
    # Step 1: Accept the connection — REQUIRED before sending or receiving
    await websocket.accept()

    # Step 2: Optionally send a welcome message
    await websocket.send_text("Connected! Send messages and I'll echo them.")

    try:
        # Step 3: Message loop — runs until connection closes
        while True:
            # receive_text() blocks until a message arrives
            message = await websocket.receive_text()
            logger.info(f"Received: {message!r}")

            # Handle special commands
            if message == "disconnect":
                await websocket.close(
                    code=status.WS_1000_NORMAL_CLOSURE,
                    reason="Client requested disconnect",
                )
                return   # exit the function — connection is closed

            if "bad" in message.lower():
                # Close with policy violation — message was unacceptable
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Message contains prohibited content",
                )

            # Echo the message back
            await websocket.send_text(f"Echo: {message}")

    except WebSocketDisconnect:
        # This is raised when the CLIENT closes the connection
        # (closes browser tab, network drops, client calls ws.close())
        logger.info("Client disconnected normally")
    # WebSocketException closes the connection automatically — no catch needed
```

---

## 🔐 Authenticated WebSockets

WebSockets can't use cookie-based auth or custom headers from the browser (browsers don't support custom headers on WebSocket connections). The standard approach: pass the token as a query parameter or in the first message.

```python
from fastapi import WebSocket, Depends, Query
from typing import Annotated
from auth.jwt import decode_token
from models import User
from database import get_session

async def get_ws_user(
    token: str = Query(...),    # token passed as ?token=xxx in the WebSocket URL
    session = Depends(get_session),
) -> User:
    """
    Authenticate a WebSocket connection via token query param.
    Called before the WebSocket handler runs.
    If auth fails, FastAPI rejects the connection with 403.
    """
    try:
        username = decode_token(token)
    except Exception:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token",
        )

    user = session.query(User).filter(User.username == username).first()
    if not user:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User not found",
        )
    return user

# Client connects with: ws://localhost:8000/chat?token=eyJhbGc...
@app.websocket("/chat")
async def authenticated_chat(
    websocket: WebSocket,
    user: Annotated[User, Depends(get_ws_user)],   # auth runs before accept()
):
    await websocket.accept()
    await websocket.send_text(f"Welcome, {user.username}!")

    try:
        # iter_text() is cleaner than while True + receive_text()
        # It auto-handles WebSocketDisconnect by stopping iteration
        async for message in websocket.iter_text():
            await websocket.send_text(f"{user.username}: {message}")
    except WebSocketDisconnect:
        logger.info(f"{user.username} disconnected")
```

---

## 🏠 Multi-Room Chat — ConnectionManager

Managing multiple clients across multiple rooms requires tracking who's connected where. The `ConnectionManager` class handles this.

```python
# chat/manager.py
from fastapi import WebSocket
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections organized by room.
    Thread-safe for asyncio (single-threaded event loop).
    """

    def __init__(self):
        # room_id → list of active WebSocket connections
        self.rooms: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        """Accept a connection and add it to the room."""
        await websocket.accept()
        self.rooms[room_id].append(websocket)
        # Tell everyone in the room someone joined
        await self.broadcast(
            room_id=room_id,
            message=f"📢 {username} joined the room",
            exclude=None,    # include everyone, even the new joiner
        )

    async def disconnect(self, websocket: WebSocket, room_id: str, username: str):
        """Remove a connection from the room."""
        if websocket in self.rooms[room_id]:
            self.rooms[room_id].remove(websocket)
        # Clean up empty rooms
        if not self.rooms[room_id]:
            del self.rooms[room_id]
        # Notify remaining users
        await self.broadcast(
            room_id=room_id,
            message=f"👋 {username} left the room",
        )

    async def send_personal(self, websocket: WebSocket, message: str):
        """Send a message to one specific client."""
        await websocket.send_text(message)

    async def broadcast(
        self,
        room_id: str,
        message: str,
        exclude: WebSocket | None = None,
    ):
        """
        Send a message to all clients in a room.
        exclude: skip this connection (e.g. don't echo to sender)
        """
        dead_connections = []
        for connection in self.rooms.get(room_id, []):
            if connection is exclude:
                continue
            try:
                await connection.send_text(message)
            except Exception:
                # Connection died unexpectedly — mark for removal
                dead_connections.append(connection)

        # Clean up dead connections
        for dead in dead_connections:
            if dead in self.rooms[room_id]:
                self.rooms[room_id].remove(dead)

    def room_member_count(self, room_id: str) -> int:
        return len(self.rooms.get(room_id, []))


# Singleton — one manager shared across all requests
manager = ConnectionManager()
```

```python
# chat/endpoints.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Annotated
from .manager import manager

router = APIRouter()

@router.websocket("/rooms/{room_id}")
async def room_chat(
    websocket: WebSocket,
    room_id: str,
    user: Annotated[User, Depends(get_ws_user)],
):
    """
    Multi-room chat endpoint.
    Messages are broadcast to all users in the same room.
    """
    await manager.connect(websocket, room_id, user.username)

    try:
        async for raw_message in websocket.iter_text():
            # Format: "username: message" for display
            formatted = f"{user.username}: {raw_message}"

            # Broadcast to everyone EXCEPT the sender (they see it locally)
            await manager.broadcast(
                room_id=room_id,
                message=formatted,
                exclude=websocket,
            )

            # Optionally: send confirmation to sender
            await manager.send_personal(
                websocket,
                f"✓ Delivered to {manager.room_member_count(room_id) - 1} others",
            )

    except WebSocketDisconnect:
        await manager.disconnect(websocket, room_id, user.username)

    except Exception as e:
        logger.error(f"Unexpected error in room {room_id}: {e}")
        await manager.disconnect(websocket, room_id, user.username)
```

---

## 🔒 Premium-Only Rooms

```python
@router.websocket("/rooms/vip/{room_id}")
async def vip_room(
    websocket: WebSocket,
    room_id: str,
    user: Annotated[User, Depends(get_ws_user)],
):
    """Premium-only room — closes immediately if user doesn't have access."""
    if user.role not in ("premium", "admin"):
        # Close before accepting with policy violation
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Premium membership required",
        )
        return   # ← IMPORTANT: return after close

    await manager.connect(websocket, f"vip-{room_id}", user.username)

    try:
        async for message in websocket.iter_text():
            await manager.broadcast(
                room_id=f"vip-{room_id}",
                message=f"[VIP] {user.username}: {message}",
                exclude=websocket,
            )
    except WebSocketDisconnect:
        await manager.disconnect(websocket, f"vip-{room_id}", user.username)
```

---

## 📊 Benchmarking WebSocket Throughput

```python
# benchmark_websocket.py
import asyncio
import websockets
import time
import statistics

async def measure_throughput(
    url: str,
    num_messages: int = 1000,
    message_size: int = 100,
) -> dict:
    """Measure how many messages per second a WebSocket endpoint can handle."""
    message = "x" * message_size   # fixed-size payload

    latencies = []
    start = time.perf_counter()

    async with websockets.connect(url) as ws:
        # Receive welcome message
        await ws.recv()

        for i in range(num_messages):
            send_time = time.perf_counter()
            await ws.send(f"message {i}: {message}")
            await ws.recv()           # wait for echo
            latencies.append((time.perf_counter() - send_time) * 1000)  # ms

    total_time = time.perf_counter() - start

    return {
        "total_messages": num_messages,
        "total_time_s": round(total_time, 2),
        "messages_per_second": round(num_messages / total_time),
        "latency_p50_ms": round(statistics.median(latencies), 2),
        "latency_p95_ms": round(sorted(latencies)[int(num_messages * 0.95)], 2),
        "latency_p99_ms": round(sorted(latencies)[int(num_messages * 0.99)], 2),
    }

if __name__ == "__main__":
    result = asyncio.run(measure_throughput("ws://localhost:8000/ws", num_messages=5000))
    for key, value in result.items():
        print(f"{key}: {value}")
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| `await websocket.accept()` must be first | Can't send or receive before accepting the handshake |
| `WebSocketDisconnect` vs `WebSocketException` | Disconnect = client closed cleanly. Exception = close with a specific error code |
| `async for message in websocket.iter_text()` | Cleaner than `while True: receive_text()` — handles disconnect automatically |
| Token in query param, not header | Browsers can't set custom headers on WebSocket connections — use `?token=xxx` |
| `exclude=websocket` in broadcast | Don't echo messages back to the sender — they already see it locally |
| Clean up dead connections after broadcast | `send_text()` can fail if a connection drops mid-broadcast — catch and remove |
| `await websocket.close()` then `return` | Close then immediately return — don't continue running after closing |
