from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, database, auth

router = APIRouter(
    prefix="/history",
    tags=["history"],
    responses={404: {"detail": "Not found"}},
)

@router.get("/{room_id}", response_model=List[models.MessageResponse])
def get_history(room_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    messages = db.query(models.Message).filter(models.Message.room_id == room_id).order_by(models.Message.timestamp).all()
    # Enrich with username
    for msg in messages:
        msg.username = msg.user.username
    return messages
