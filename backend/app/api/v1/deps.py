from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..models.meeting import Meeting
from ..schemas.meeting import MeetingCreate

async def get_meeting(meeting_id: int, db: Session = Depends(get_db)) -> Meeting:
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

async def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)) -> Meeting:
    db_meeting = Meeting(**meeting.dict())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting