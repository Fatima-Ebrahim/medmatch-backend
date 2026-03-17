from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base

class MenteeProfile(Base):
    __tablename__ = 'mentee_profiles'
    user_id              = Column(Integer, ForeignKey('users.id'), primary_key=True)
    department           = Column(String, nullable=True)
    career_stage         = Column(String, nullable=True)
    research_interests   = Column(Text, nullable=True)
    goals                = Column(Text, nullable=True)
    desired_skills       = Column(Text, nullable=True)
    cv_file              = Column(String, nullable=True)
    embedding            = Column(Text, nullable=True)
    admin_notes          = Column(Text, nullable=True)