from pydantic import BaseModel
from typing import Optional

# ── Mentor ──────────────────────────────────────────────────────
class MentorProfileUpdate(BaseModel):
    department:     Optional[str] = None
    expertise_tags: Optional[str] = None
    bio:            Optional[str] = None
    pubmed_url:     Optional[str] = None
    max_mentees:    Optional[int] = None
    availability:   Optional[bool] = None

class MentorProfileOut(BaseModel):
    user_id:        int
    department:     Optional[str]
    expertise_tags: Optional[str]
    bio:            Optional[str]
    pubmed_url:     Optional[str]
    max_mentees:    int
    availability:   bool
    model_config = {'from_attributes': True}

# ── Mentee ──────────────────────────────────────────────────────
class MenteeProfileUpdate(BaseModel):
    department:         Optional[str] = None
    career_stage:       Optional[str] = None
    research_interests: Optional[str] = None
    goals:              Optional[str] = None
    desired_skills:     Optional[str] = None

class MenteeProfileOut(BaseModel):
    user_id:            int
    department:         Optional[str]
    career_stage:       Optional[str]
    research_interests: Optional[str]
    goals:              Optional[str]
    desired_skills:     Optional[str]
    cv_file:            Optional[str]
    model_config = {'from_attributes': True}

# ── Investigator ────────────────────────────────────────────────
class InvestigatorProfileUpdate(BaseModel):
    department:     Optional[str] = None
    title:          Optional[str] = None
    expertise_tags: Optional[str] = None
    bio:            Optional[str] = None
    pubmed_url:     Optional[str] = None