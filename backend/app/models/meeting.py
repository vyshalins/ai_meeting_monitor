from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ActionItem(BaseModel):
    id: int
    description: str
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: bool = False

class Meeting(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    date: datetime
    participants: List[str]
    action_items: List[ActionItem] = []