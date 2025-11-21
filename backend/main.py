from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import asyncio
from . import models, database, auth, router_rooms, router_history
from .websocket_manager import manager
from .kafka_service import kafka_service
import psycopg2
from dotenv import load_dotenv
import os


app = FastAPI(title="Real-Time Chat App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
models.Base.metadata.create_all(bind=database.engine)

# Routers
app.include_router(auth.router)
app.include_router(router_rooms.router)
app.include_router(router_history.router)

# Kafka Startup/Shutdown
@app.on_event("startup")
async def startup_event():
    kafka_service.start()
    # Start consuming in background
    import threading
    t = threading.Thread(target=kafka_service.consume_messages, args=("chat_messages", process_kafka_message))
    t.daemon = True
    t.start()

@app.on_event("shutdown")
def shutdown_event():
    kafka_service.stop()

async def process_kafka_message(msg):
    # msg is a dict with room_id, content, username, etc.
    # Broadcast to WebSocket clients in that room
    room_id = msg.get("room_id")
    if room_id:
        await manager.broadcast(json.dumps(msg), room_id)

@app.websocket("/ws/{room_id}/{token}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str, db: Session = Depends(database.get_db)):
    # Verify token
    try:
        user = await auth.get_current_user(token, db)
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            # When receiving a message from WS, save to DB and produce to Kafka
            message_data = json.loads(data)
            content = message_data.get("content")
            
            # Save to DB
            db_msg = models.Message(content=content, user_id=user.id, room_id=room_id)
            db.add(db_msg)
            db.commit()
            
            # Produce to Kafka
            kafka_msg = {
                "room_id": room_id,
                "content": content,
                "username": user.username,
                "user_id": user.id,
                "timestamp": str(db_msg.timestamp)
            }
            await kafka_service.send_message("chat_messages", kafka_msg)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
