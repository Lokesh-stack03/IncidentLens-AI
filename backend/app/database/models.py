# id,name,base_url,http_method,is_active ,created_att
from backend.app.database.database import Base
from datetime import datetime
from sqlalchemy import Column,Integer,String,Boolean,DateTime
class Integration(Base):
    __tablename__="integrations"
    id=Column(Integer,primary_key=True, index=True)
    name=Column(String(100),nullable=False)
    base_url=Column(String(500),nullable=False)
    http_method=Column(String(10),default="GET",nullable=False)
    is_active=Column(Boolean,default=True)
    created_at=Column(DateTime,default=datetime.utcnow)
