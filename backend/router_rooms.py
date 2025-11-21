from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, database, auth

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
    responses={404: {"detail": "Not found"}},
)

@router.post("/", response_model=models.RoomResponse)
def create_room(room: models.RoomCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_room = db.query(models.Room).filter(models.Room.name == room.name).first()
    if db_room:
        raise HTTPException(status_code=400, detail="Room already exists")
    new_room = models.Room(name=room.name)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

@router.get("/", response_model=List[models.RoomResponse])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    rooms = db.query(models.Room).offset(skip).limit(limit).all()
    return rooms
