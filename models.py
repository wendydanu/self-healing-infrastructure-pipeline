from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class IncidentLog(Base):
    __tablename__ = "incident_logs"

    id = Column(Integer, primary_key=True, index=True)
    error_log = Column(Text, nullable=False)
    broken_code = Column(Text, nullable=False)
    
    error_analysis = Column(Text, nullable=True)
    suggested_patch = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)