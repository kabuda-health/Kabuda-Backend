from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.user import Base

class DailyHealthData(Base):
    __tablename__ = "daily_health_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date = Column(Date, nullable=False)

    weight_kg = Column(Float, nullable=True)
    height_m = Column(Float, nullable=True)
    resting_hr = Column(Float, nullable=True)
    sleep_duration_hr = Column(Float, nullable=True)
    sleep_quality = Column(String, nullable=True)
    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
