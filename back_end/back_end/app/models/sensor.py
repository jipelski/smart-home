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

SensorDataOut = Union[BME688Data]