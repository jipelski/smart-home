from pydantic import BaseModel, Field
from typing import Literal, Union
from datetime import datetime


class SensorDataBase(BaseModel):
    sensor_id: str
    timestamp: datetime

class BME688Data(SensorDataBase):
    sensor_type: Literal['BME688']
    temperature: float
    humidity: float
    pressure: float
    gas_resistance: float

class BME688AggrData(SensorDataBase):
    sensor_type: Literal['BME688']
    avg_temperature: float
    max_temperature: float
    min_temperature: float
    avg_humidity: float
    max_humidity: float
    min_humidity: float
    avg_pressure: float
    max_pressure: float
    min_pressure: float
    avg_gas_resistance: float
    max_gas_resistance: float
    min_gas_resistance: float

SensorDataOut = Union[BME688Data]

AggrDataOut = Union[BME688AggrData]