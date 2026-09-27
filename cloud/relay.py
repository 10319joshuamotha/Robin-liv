"""Small provider-neutral WebSocket relay for Robin companion devices.

This relay transports authenticated JSON tasks/results; it never executes them.
Run behind TLS in production and place it behind a reverse proxy/rate limiter.
"""

from __future__ import annotations

import asyncio
import os
from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(docs_url=None, redoc_url=None)
_rooms: dict[str, set[WebSocket]] = defaultdict(set)
_token = os.environ.get("ROBIN_RELAY_TOKEN")


@app.websocket("/ws/{device_id}")
async def relay(websocket: WebSocket, device_id: str, token: str = ""):
    if not _token or token != _token:
        await websocket.close(code=4001)
        return
    await websocket.accept()
    room = _rooms[device_id]
    room.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            dead = set()
            for peer in room:
                if peer is websocket:
                    continue
                try:
                    await peer.send_text(message)
                except Exception:
                    dead.add(peer)
            room.difference_update(dead)
    except WebSocketDisconnect:
        pass
    finally:
        room.discard(websocket)
        if not room:
            _rooms.pop(device_id, None)
