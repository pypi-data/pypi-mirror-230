import uuid
from typing import Optional, Union, List

from .models.cloud_models import SaveProtocolRequest
from .models.database import DeviceModel, DeviceLinkModel, DeviceStatisticModel, ProtocolModel, ProtocolLinkModel, \
    UserModel
from .models.admin_cloud_models import DeviceRequest, UserRequest
from .base_client import BaseClient


class AdminLabClient(BaseClient):

    def __init__(self, url, token):
        super().__init__(url, token)

    def login_user(self, user_id: uuid.UUID) -> str:
        response = self.post(f"/admin/auth/token",
                             headers={"Authorization": f"Bearer {self.token}"},
                             params={"user_id": user_id})
        return response.json().get("access_token")

    def login_device(self, user_id: uuid.UUID, device_id: uuid.UUID) -> str:
        response = self.post(f"/admin/auth/device",
                             headers={"Authorization": f"Bearer {self.token}"},
                             params={"user_id": user_id, "device_id": device_id})
        return response.json().get("access_token")

    def get_users(self, user_id: Optional[uuid.UUID] = None) -> Union[List[UserModel], UserModel]:
        params = {}
        if user_id:
            params["user_id"] = user_id
        response = self.get(f"/admin/user",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params=params)
        response_dict = response.json()
        if type(response_dict) == list:
            return [UserModel.parse_obj(r) for r in response_dict]
        else:
            return UserModel.parse_obj(response_dict)

    def add_user(self, add_user_request: UserRequest) -> UserModel:
        response = self.post(f"/admin/user", json=add_user_request.dict(),
                             headers={"Authorization": f"Bearer {self.token}"})
        return UserModel.parse_obj(response.json())

    def delete_user(self, user_id: uuid.UUID):
        self.delete(f"/admin/user",
                    headers={"Authorization": f"Bearer {self.token}"},
                    params={"user_id": user_id})

    def update_user(self, user_id: uuid.UUID, add_user_request: UserRequest) -> UserModel:
        response = self.post(f"/admin/user/update", json=add_user_request.dict(),
                             headers={"Authorization": f"Bearer {self.token}"},
                             params={"user_id": user_id})
        return UserModel.parse_obj(response.json())

    def get_protocol(self, protocol_id: Optional[uuid.UUID] = None) -> Union[ProtocolModel, List[ProtocolModel]]:
        params = {}
        if protocol_id:
            params["protocol_id"] = protocol_id
        response = self.get(f"/admin/protocol",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params=params)
        response_dict = response.json()
        if type(response_dict) == list:
            return [ProtocolModel.parse_obj(r) for r in response_dict]
        else:
            return ProtocolModel.parse_obj(response_dict)

    def store_protocol(self, protocol_request: SaveProtocolRequest) -> ProtocolModel:
        response = self.post(f"/admin/protocol",
                             headers={"Authorization": f"Bearer {self.token}"},
                             json=protocol_request.dict())
        return ProtocolModel.parse_obj(response.json())

    def link_protocol(self, protocol_id: uuid.UUID, user_id: uuid.UUID) -> ProtocolLinkModel:
        response = self.post(f"/admin/protocol/link",
                             headers={"Authorization": f"Bearer {self.token}"},
                             params={"protocol_id": protocol_id, "user_id": user_id})
        return ProtocolLinkModel.parse_obj(response.json())

    def remove_link_protocol(self, protocol_link_id: uuid.UUID):
        self.delete(f"/admin/protocol/link",
                    headers={"Authorization": f"Bearer {self.token}"},
                    params={"protocol_link_id": protocol_link_id})

    def get_devices(self, device_id: Optional[uuid.UUID] = None) -> Union[List[DeviceModel], DeviceModel]:
        params = {}
        if device_id:
            params["device_id"] = device_id
        response = self.get(f"/admin/device",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params=params)
        response_dict = response.json()
        if type(response_dict) == list:
            return [DeviceModel.parse_obj(r) for r in response_dict]
        else:
            return DeviceModel.parse_obj(response_dict)

    def add_device(self, add_device_request: DeviceRequest) -> DeviceModel:
        response = self.post(f"/admin/device", json=add_device_request.dict(),
                             headers={"Authorization": f"Bearer {self.token}"})
        return DeviceModel.parse_obj(response.json())

    def delete_device(self, device_id: uuid.UUID):
        self.delete(f"/admin/device",
                    headers={"Authorization": f"Bearer {self.token}"},
                    params={"device_id": device_id})

    def update_device(self, device_id: uuid.UUID, add_device_request: DeviceRequest) -> DeviceModel:
        response = self.post(f"/admin/device/update", json=add_device_request.dict(),
                             headers={"Authorization": f"Bearer {self.token}"},
                             params={"device_id": device_id})
        return DeviceModel.parse_obj(response.json())

    def link_device(self, device_id: uuid.UUID, user_id: uuid.UUID) -> DeviceLinkModel:
        response = self.post(f"/admin/device/link",
                             headers={"Authorization": f"Bearer {self.token}"},
                             params={"device_id": device_id, "user_id": user_id})
        return DeviceLinkModel.parse_obj(response.json())

    def remove_link_device(self, device_link_id: uuid.UUID):
        self.delete(f"/admin/device/link",
                    headers={"Authorization": f"Bearer {self.token}"},
                    params={"device_link_id": device_link_id})

    def get_device_statistics(self, device_id: Optional[uuid.UUID] = None) -> List[DeviceStatisticModel]:
        params = {}
        if device_id:
            params["device_id"] = device_id
        response = self.get(f"/admin/device/statistic",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params=params)
        return [DeviceStatisticModel.parse_obj(r) for r in response.json()]
