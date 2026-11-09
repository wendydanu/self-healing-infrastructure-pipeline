from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class IncidentLog(Base):
    __tablename__ = "incident_logs"

    id = Column(Integer, primary_key=True, index=True)
    error_log = Column(Text, nullable=False)
    broken_code = Column(Text, nullable=False)
    error_analysis = Column(Text, nullable=True)
    suggested_patch = Column(Text, nullable=True)
    target_file = Column(String(255), nullable=False, default="server_math.py")
    created_at = Column(DateTime(timezone=True), server_default=func.now())