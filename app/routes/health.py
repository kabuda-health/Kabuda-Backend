from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import UserDep, get_db
from app.models.health import DailyHealthData

router = APIRouter()


class DailyHealthDataIn(BaseModel):
    date: date
    weight_kg: Optional[float] = None
    height_m: Optional[float] = None
    resting_hr: Optional[float] = None
    sleep_duration_hr: Optional[float] = None
    sleep_quality: Optional[str] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None


@router.post("/health/")
async def upload_health_data(
    daily_data: List[DailyHealthDataIn],
    db: Annotated[AsyncSession, Depends(get_db)],
    user: UserDep,
) -> dict:
    for entry in daily_data:
        db.add(
            DailyHealthData(
                user_id=user.id,
                date=entry.date,
                weight_kg=entry.weight_kg,
                height_m=entry.height_m,
                resting_hr=entry.resting_hr,
                sleep_duration_hr=entry.sleep_duration_hr,
                sleep_quality=entry.sleep_quality,
                systolic_bp=entry.systolic_bp,
                diastolic_bp=entry.diastolic_bp,
            )
        )
    await db.commit()
    return {"message": "success"}
