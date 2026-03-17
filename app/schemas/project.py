from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    title:             str
    description:       str
    required_skills:   Optional[str] = None
    career_stage_pref: Optional[str] = None
    duration:          Optional[str] = None
    positions:         int = 1

class ProjectUpdate(BaseModel):
    title:             Optional[str] = None
    description:       Optional[str] = None
    required_skills:   Optional[str] = None
    career_stage_pref: Optional[str] = None
    duration:          Optional[str] = None
    positions:         Optional[int] = None

class ProjectOut(BaseModel):
    id:               int
    investigator_id:  int
    title:            str
    description:      str
    required_skills:  Optional[str]
    career_stage_pref: Optional[str]
    duration:         Optional[str]
    positions:        int
    status:           str
    created_at:       datetime
    model_config = {'from_attributes': True}