from fastapi import APIRouter, HTTPException
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
    try:
        return calculate_sustain_tps(body.tps, body.minutes)
    except ZeroDivisionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/duration")
def fixed_dataset_duration(body: DurationRequest):
    try:
        return calculate_duration(body.transactions, body.tps)
    except ZeroDivisionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
