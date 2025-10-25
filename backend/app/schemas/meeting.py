from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(MeetingBase):
    pass

class Meeting(MeetingBase):
    id: int

    class Config:
        orm_mode = True

class ActionItemBase(BaseModel):
    description: str
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

class ActionItemCreate(ActionItemBase):
    pass

class ActionItemUpdate(ActionItemBase):
    pass

class ActionItem(ActionItemBase):
    id: int
    meeting_id: int

    class Config:
        orm_mode = True

class MeetingResponse(BaseModel):
    meeting: Meeting
    action_items: List[ActionItem] = []