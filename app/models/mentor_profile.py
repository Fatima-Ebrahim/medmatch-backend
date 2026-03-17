from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from app.database import Base

class MentorProfile(Base):
    __tablename__ = 'mentor_profiles'
    user_id        = Column(Integer, ForeignKey('users.id'), primary_key=True)
    department     = Column(String, nullable=True)
    expertise_tags = Column(Text, nullable=True)
    bio            = Column(Text, nullable=True)
    pubmed_url     = Column(String, nullable=True)
    max_mentees    = Column(Integer, default=3)
    availability   = Column(Boolean, default=True)
    embedding      = Column(Text, nullable=True)
    admin_notes    = Column(Text, nullable=True)