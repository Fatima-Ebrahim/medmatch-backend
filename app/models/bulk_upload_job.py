from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base

class BulkUploadJob(Base):
    __tablename__ = 'bulk_upload_jobs'
    id             = Column(Integer, primary_key=True, index=True)
    admin_id       = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_rows     = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    error_log      = Column(Text, default='[]')  # JSON list of errors
    status         = Column(String, default='queued')  # queued, processing, done, failed
    created_at     = Column(DateTime(timezone=True), server_default=func.now())