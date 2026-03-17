from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func
from app.database import Base

class Match(Base):
    __tablename__ = 'matches'
    id         = Column(Integer, primary_key=True, index=True)
    mentee_id  = Column(Integer, ForeignKey('users.id'), nullable=False)
    mentor_id  = Column(Integer, ForeignKey('users.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    score      = Column(Float, nullable=False)
    status     = Column(String, default='pending') # pending, active, declined, expired, admin_review
    admin_note = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)