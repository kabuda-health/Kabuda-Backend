from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String

from app.models.user import Base


class DailyHealthData(Base):
    __tablename__ = "daily_health_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    steps = Column(Integer, nullable=True)
    calories = Column(Float, nullable=True)
    distance = Column(Float, nullable=True)
    active_minutes = Column(Integer, nullable=True)
    heart_rate = Column(Float, nullable=True)
    sleep_duration = Column(Float, nullable=True)
    sleep_quality = Column(Float, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
