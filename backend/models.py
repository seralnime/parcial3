from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))

    user = relationship("User")
    room = relationship("Room")

class RoomMember(Base):
    __tablename__ = "room_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))

    user = relationship("User")
    room = relationship("Room")

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class RoomCreate(BaseModel):
    name: str

class RoomResponse(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    content: str
    room_id: int

class MessageResponse(BaseModel):
    id: int
    content: str
    timestamp: datetime
    user_id: int
    room_id: int
    username: str # Added for convenience
    class Config:
        orm_mode = True
