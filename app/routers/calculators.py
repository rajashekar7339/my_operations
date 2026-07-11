from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.calculators import calculate_duration, calculate_sustain_tps

router = APIRouter(prefix="/api", tags=["calculators"])


class SustainRequest(BaseModel):
    tps: float = Field(..., gt=0, description="Transactions per second")
    minutes: float = Field(..., gt=0, description="Duration in minutes")


class DurationRequest(BaseModel):
    transactions: float = Field(..., gt=0, description="Total transaction count")
    tps: float = Field(..., gt=0, description="Transactions per second")


@router.post("/sustain")
def sustain_tps(body: SustainRequest):
    return calculate_sustain_tps(body.tps, body.minutes)


@router.post("/duration")
def fixed_dataset_duration(body: DurationRequest):
    return calculate_duration(body.transactions, body.tps)
