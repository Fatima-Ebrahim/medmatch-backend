from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base

class InvestigatorProfile(Base):
    __tablename__ = 'investigator_profiles'
    user_id        = Column(Integer, ForeignKey('users.id'), primary_key=True)
    department     = Column(String, nullable=True)
    title          = Column(String, nullable=True)
    expertise_tags = Column(Text, nullable=True)
    bio            = Column(Text, nullable=True)
    pubmed_url     = Column(String, nullable=True)