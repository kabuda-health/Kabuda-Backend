from fastapi import APIRouter, Depends
from typing import Optional, List, Annotated
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.health import DailyHealthData
from pydantic import BaseModel

router = APIRouter()

class DailyHealthDataIn(BaseModel):
    date: date
    weight_kg: Optional[float]
    height_m: Optional[float]
    resting_hr: Optional[float]
    sleep_duration_hr: Optional[float]
    sleep_quality: Optional[str]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]

@router.post("/health-upload/")
async def upload_health_data(
    daily_data: List[DailyHealthDataIn],
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)]
) -> dict:
    for entry in daily_data:
        db.add(DailyHealthData(
            user_id=user.id,
            date=entry.date,
            weight_kg=entry.weight_kg,
            height_m=entry.height_m,
            resting_hr=entry.resting_hr,
            sleep_duration_hr=entry.sleep_duration_hr,
            sleep_quality=entry.sleep_quality,
            systolic_bp=entry.systolic_bp,
            diastolic_bp=entry.diastolic_bp
        ))
    await db.commit()
    return {"message": "success"}
