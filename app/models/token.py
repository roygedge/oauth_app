from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from ..database import Base

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    realm_id = Column(String)
    expires_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, default=datetime.now)

    def is_expired(self):
        return datetime.now() >= self.expires_at