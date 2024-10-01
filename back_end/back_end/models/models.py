from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class SensorData(BaseModel):
    sensor_id: str
    sensor_type: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]