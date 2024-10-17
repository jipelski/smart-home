from fastapi import APIRouter, Query
from typing import Optional
import datetime
from models.sensor import SensorDataOut, AggrDataOut
from services.db_service import fetch_sensor_data, fetch_sensor_data_filtered, fetch_latest_sensor_data, fetch_aggregated_data

router = APIRouter()

@router.get("/sensor-data/{sensor_type}/{sensor_id}", response_model=list[SensorDataOut])
async def get_sensor_data(sensor_id: str, sensor_type: str):
    return await fetch_sensor_data(sensor_id, sensor_type)

@router.get("/sensor-data/{sensor_type}", response_model=list[SensorDataOut])
async def get_sensor_data_filtered(
    sensor_type: str,
    sensor_id: Optional[str] = None,
    start_time: Optional[datetime.datetime] = None,
    end_time: Optional[datetime.datetime] = None,
    limit: Optional[int] = Query(100, ge=1),
):
    return await fetch_sensor_data_filtered(sensor_id, sensor_type, start_time, end_time, limit)

@router.get("/sensor-data-latest/{sensor_type}/{sensor_id}", response_model=SensorDataOut)
async def get_latest_sensor_data(sensor_id: str, sensor_type: str):
    return await fetch_latest_sensor_data(sensor_id, sensor_type)

@router.get("/aggregated-sensor-data/{sensor_type}/{sensor_id}", response_model=AggrDataOut)
async def get_aggreated_data(sensor_id: str, sensor_type: str):
    return await fetch_aggregated_data(sensor_id, sensor_type)