from pydantic import BaseModel

class ConnectDeviceRequest(BaseModel):
    peripheral_mac: str
    service_uuid: str
    characteristic_uuid: str
    structure: str
    device_type: str