from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base


class Beverage(Base):
    __tablename__ = "beverages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # bier, wein, spirituose, sonstiges
    volume = Column(Float, nullable=False)  # liters
    price = Column(Float, nullable=False)  # euros
    store = Column(String, nullable=False)
    alcohol_content = Column(Float, nullable=False)  # percent
    created_at = Column(DateTime, default=datetime.utcnow)
