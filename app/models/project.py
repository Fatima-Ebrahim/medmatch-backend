from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base

class Project(Base):
    __tablename__ = 'projects'
    id                = Column(Integer, primary_key=True, index=True)
    investigator_id   = Column(Integer, ForeignKey('users.id'), nullable=False)
    title             = Column(String, nullable=False)
    description       = Column(Text, nullable=False)
    required_skills   = Column(Text, nullable=True)
    career_stage_pref = Column(String, nullable=True)
    duration          = Column(String, nullable=True)
    positions         = Column(Integer, default=1)
    status            = Column(String, default='draft') # draft, open, closed
    embedding         = Column(Text, nullable=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    
    