# id,name,base_url,http_method,is_active ,created_att
from backend.app.database.database import Base
from datetime import datetime
from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Text
class Integration(Base):
    __tablename__="integrations"
    id=Column(Integer,primary_key=True, index=True)
    name=Column(String(100),nullable=False)
    base_url=Column(String(500),nullable=False)
    http_method=Column(String(10),default="GET",nullable=False)
    is_active=Column(Boolean,default=True)
    created_at=Column(DateTime,default=datetime.utcnow)
class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)

    title = Column(String(255), nullable=False)
    error_message = Column(Text, nullable=False)
    status_code = Column(Integer, nullable=True)
    endpoint = Column(String(500), nullable=True)

    status = Column(String(50), nullable=False, default="OPEN")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
