# app/schemas/match.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchOut(BaseModel):
    id:         int
    mentee_id:  int
    mentor_id:  Optional[int]
    project_id: Optional[int]
    score:      float
    status:     str
    admin_note: Optional[str]
    created_at: datetime
    expires_at: datetime
    model_config = {'from_attributes': True}

class AdminReviewIn(BaseModel):
    note:    str
    confirm: bool  # True = confirm match, False = reject it