from fastapi import APIRouter, HTTPException
from services.mqtt_service import publish_command
from models.hub import ConnectDeviceRequest

router = APIRouter()

@router.post("/hubs/{hub_id}/connect_device")
async def connect_device(hub_id: str, request: ConnectDeviceRequest):
    command = {
        "command": "connect_device",
        "peripheral_mac": request.peripheral_mac,
        "service_uuid": request.service_uuid,
        "characteristic_uuid": request.characteristic_uuid,
        "structure": request.structure,
        "type": request.device_type
    }
    try:
        await publish_command(hub_id, command)
        return {"status": "Connect command sent", "hub_id": hub_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hubs/{hub_id}/disconnect_device")
async def disconnect_device(hub_id: str, peripheral_mac: str):
    command = {
        "command": "disconnect_device",
        "peripheral_mac": peripheral_mac
    }
    try:
        await publish_command(hub_id, command)
        return {"status": "Disconnect command sent", "hub_id": hub_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
