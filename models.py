from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True, index=True)  
    url = Column(String, nullable=False, unique=True)  
    interval = Column(Integer, nullable=False, default=60) 
    notifications_enabled = Column(Boolean, default=True) 
    history = relationship("SiteHistory", back_populates="site", cascade="all, delete-orphan") 

class SiteHistory(Base):
    __tablename__ = "checks"
    id = Column(Integer, primary_key=True, index=True)  
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)  
    status_code = Column(Integer, nullable=True)  
    response_time = Column(Integer, nullable=True) 
    checked_at = Column(DateTime, default=datetime.datetime.utcnow) 
    site = relationship("Site", back_populates="history")  
    content_hash = Column(String, nullable=True)  