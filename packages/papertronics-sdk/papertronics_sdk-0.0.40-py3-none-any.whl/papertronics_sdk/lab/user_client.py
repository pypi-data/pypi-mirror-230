import time
import uuid
from typing import Optional, List, Union

from .models.database import DeviceModel, UserModel, ProtocolModel, ExperimentModel, ExperimentStatus
from .models.cloud_models import SaveProtocolRequest, ProtocolTestResponse, ExperimentStartRequest, \
    ExperimentEditRequest
from .base_client import BaseClient


class UserLabClient(BaseClient):

    def authenticate(self, email, password):
        response = self.post(f"/auth/token", data=dict(username=email, password=password), include_token=False)
        self.token = response.json().get("access_token")
        return self.token

    def authenticate_device(self, device_id: uuid.UUID):
        response = self.post(f"/auth/device",
                             headers={"Authorization": f"Bearer {self.token}"},
                             params={"device_id": device_id})
        self.token = response.json().get("access_token")
        return self.token

    def download_data(self):
        return "not implemented"

    def download_image(self,
                       blob_name: str):
        return "not implemented"

    def get_device_info(self) -> DeviceModel:
        response = self.get(f"/device",
                            headers={"Authorization": f"Bearer {self.token}"})
        return DeviceModel.parse_obj(response.json())

    def get_devices(self) -> List[DeviceModel]:
        response = self.get(f"/device/all",
                            headers={"Authorization": f"Bearer {self.token}"})
        return [DeviceModel.parse_obj(r) for r in response.json()]

    def get_user_info(self) -> UserModel:
        response = self.get(f"/user",
                            headers={"Authorization": f"Bearer {self.token}"})
        return UserModel.parse_obj(response.json())

    def store_protocol(self, protocol_request: SaveProtocolRequest) -> ProtocolModel:
        response = self.post(f"/protocol",
                             headers={"Authorization": f"Bearer {self.token}"},
                             json=protocol_request.dict())
        return ProtocolModel.parse_obj(response.json())

    def build_protocol(self,
                       protocol_request: SaveProtocolRequest,
                       duration: int,
                       interval: int,
                       flash: bool = True,
                       start_delay: int = 0) -> ProtocolModel:
        response = self.post(
            f"/protocol/build",
            headers={"Authorization": f"Bearer {self.token}"},
            json=protocol_request.dict(),
            params={"duration": duration, "interval": interval, "flash": flash, "start_delay": start_delay})
        return ProtocolModel.parse_obj(response.json())

    def get_protocol(self,
                     protocol_id: Optional[uuid.UUID] = None,
                     protocol_test_type: Optional[str] = None,
                     page_size: Optional[int] = None,
                     page: Optional[int] = None,
                     valid: Optional[bool] = True) -> Union[ProtocolModel, List[ProtocolModel]]:
        params = {}
        if protocol_id:
            params["protocol_id"] = protocol_id
        if protocol_test_type:
            params["protocol_test_type"] = protocol_test_type
        if page_size is not None:
            params["page_size"] = page_size
        if page is not None:
            params["page"] = page
        if valid is not None:
            params["valid"] = valid

        response = self.get(f"/protocol",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params=params)
        if type(response.json()) == list:
            return [ProtocolModel.parse_obj(r) for r in response.json()]
        else:
            return ProtocolModel.parse_obj(response.json())

    def count_protocol(self,
                       protocol_test_type: Optional[str] = None,
                       valid: Optional[bool] = True) -> int:
        params = {}
        if protocol_test_type:
            params["protocol_test_type"] = protocol_test_type
        if valid is not None:
            params["valid"] = valid

        response = self.get(f"/protocol/count",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params=params)
        return int(response.text)

    def get_protocol_test_def(self, protocol_id: uuid.UUID) -> Union[ProtocolTestResponse, str]:
        response = self.get(f"/protocol/test",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params={"protocol_id": protocol_id})
        if type(response.json()) == str:
            return response.json()
        else:
            return ProtocolTestResponse.parse_obj(response.json())

    def invalidate_protocol(self, protocol_id: uuid.UUID) -> ProtocolModel:
        response = self.delete(f"/protocol",
                               headers={"Authorization": f"Bearer {self.token}"},
                               params={"protocol_id": protocol_id})
        return ProtocolModel.parse_obj(response.json())

    def start_experiment(self, request: ExperimentStartRequest) -> ExperimentModel:
        response = self.post(f"/experiment/start",
                             headers={"Authorization": f"Bearer {self.token}",
                                      'Content-Type': 'application/json'},
                             data=request.json())
        return ExperimentModel.parse_obj(response.json())

    def cancel_experiment(self,
                          experiment_id: uuid.UUID):
        self.post(f"/experiment/cancel",
                  headers={"Authorization": f"Bearer {self.token}"},
                  json=dict(experiment_id=experiment_id))

    def get_experiments(self,
                        experiment_id: Optional[List[uuid.UUID]] = None,
                        device_id: Optional[uuid.UUID] = None,
                        order_by: str = "start_time",
                        ascending_order: bool = False,
                        page_size: Optional[int] = None,
                        page: Optional[int] = None,
                        valid: Optional[bool] = None,
                        first=True) -> Union[List[ExperimentModel], ExperimentModel]:
        params = {"order_by": order_by,
                  "ascending_order": ascending_order,
                  "first": first}
        if experiment_id:
            params["experiment_id"] = experiment_id
        if device_id:
            params["device_id"] = device_id
        if page_size is not None:
            params["page_size"] = page_size
        if page is not None:
            params["page"] = page
        if valid is not None:
            params["valid"] = valid

        response = self.get(f"/experiment",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params=params)
        if first:
            return ExperimentModel.parse_obj(response.json()[0])
        else:
            return [ExperimentModel.parse_obj(r) for r in response.json()]

    def count_experiments(self,
                          valid: Optional[bool] = None,
                          device_id: Optional[uuid.UUID] = None) -> int:
        params = {}
        if valid is not None:
            params["valid"] = valid
        if device_id is not None:
            params["device_id"] = device_id

        response = self.get(f"/experiment/count",
                            headers={"Authorization": f"Bearer {self.token}"},
                            params=params)
        return int(response.text)

    def edit_experiment_by_id(self,
                              experiment_id: uuid.UUID,
                              experiment_edit_request: ExperimentEditRequest):
        response = self.post(f"/experiment/edit",
                             headers={"Authorization": f"Bearer {self.token}"},
                             json=experiment_edit_request.dict(),
                             params={"experiment_id": experiment_id})
        return ExperimentModel.parse_obj(response.json())

    def delete_experiment_by_id(self,
                                experiment_id: uuid.UUID):
        self.delete(f"/experiment",
                    headers={"Authorization": f"Bearer {self.token}"},
                    params={"experiment_id": experiment_id})

    def perform_experiment(self, request: ExperimentStartRequest, timeout=120, check_interval=1):
        experiment = self.start_experiment(request)

        sleep_counter = 0
        images_captured = 0

        while experiment.status == ExperimentStatus.PENDING:
            time.sleep(check_interval)
            sleep_counter += check_interval
            if sleep_counter > timeout:
                raise TimeoutError("Experiment timed out. Experiment status is still PENDING.")
            experiment = self.get_experiments(experiment_id=[experiment.id], first=True)

        while experiment.status == ExperimentStatus.IN_PROGRESS or experiment.status == ExperimentStatus.STARTED:
            time.sleep(check_interval)
            experiment = self.get_experiments(experiment_id=[experiment.id], first=True)
            if len(experiment.image_extracts) > images_captured:
                images_captured = len(experiment.image_extracts)
                yield experiment

        yield experiment
