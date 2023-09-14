from typing import Optional

from pydantic import BaseModel

from papertronics_sdk.lab.models.database import DeviceCustomConfiguration


class UserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class DeviceRequest(BaseModel):
    name: Optional[str] = None
    number: Optional[int] = None
    custom_configuration: DeviceCustomConfiguration = {}
