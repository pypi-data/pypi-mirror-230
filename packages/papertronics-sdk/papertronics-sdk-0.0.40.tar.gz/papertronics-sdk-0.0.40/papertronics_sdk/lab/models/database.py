from datetime import datetime
import enum
import uuid
from typing import Optional, List, Tuple

from pydantic import BaseModel, validator

from .station_protocol import ProtocolProcessingDefinition, StationProtocol
from .generic import Point


class ORMBaseModel(BaseModel):
    class Config:
        orm_mode = True


class ExperimentStatus(str, enum.Enum):
    CREATED = "created"
    PENDING = "pending"  # experiment is pending execution
    STARTED = "started"  # device has started the experiment
    IN_PROGRESS = "in progress"  # device has started the experiment and at leas the first image has been taken
    FINISHED = "finished"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TimeWindow(str, enum.Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL_TIME = "all_time"


class ProtocolModel(ORMBaseModel):
    id: uuid.UUID
    valid: bool
    name: str
    device_type: str
    test_type: Optional[str] = None
    created_at: datetime
    device_definition: StationProtocol
    processing_definition: ProtocolProcessingDefinition


class DeviceCustomConfiguration(BaseModel):
    light_offset: Optional[Tuple[int, int, int, int]] = None
    camera_center: Optional[Point] = None

    @validator("light_offset")
    def check_light_offset(cls, v):
        if v is not None:
            for i in v:
                if not (-255 <= i <= 255):
                    raise ValueError("light offset must be between -255 and 255")
        return v


class DeviceModel(ORMBaseModel):
    id: uuid.UUID
    number: Optional[int] = None
    name: str
    created_at: datetime
    custom_configuration: DeviceCustomConfiguration = DeviceCustomConfiguration()


class DeviceLinkModel(ORMBaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    device_id: uuid.UUID

    device: DeviceModel  # TODO: test


class ProtocolLinkModel(ORMBaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    protocol_id: uuid.UUID
    usage_limit: Optional[int] = None
    limit_window: TimeWindow

    protocol: ProtocolModel  # TODO: test


class UserModel(ORMBaseModel):
    id: uuid.UUID
    name: str
    email: str
    # password: str  password is not returned

    devices: List[DeviceLinkModel] = []  # TODO: test
    protocols: List[ProtocolLinkModel] = []  # TODO: test


class DeviceStatisticModel(ORMBaseModel):  # TODO: test
    id: uuid.UUID
    device_id: uuid.UUID

    created_at: datetime
    statistic: dict


class ImageExtractModel(ORMBaseModel):
    id: Optional[uuid.UUID] = None
    experiment_id: Optional[uuid.UUID] = None

    image_key: str
    image_bucket: str
    image_number: int

    capture_time: datetime
    mask_size: float
    template_matching: bool

    red: float
    green: float
    blue: float

    lab_l: Optional[float] = None
    lab_a: Optional[float] = None
    lab_b: Optional[float] = None

    hsv_h: Optional[float] = None
    hsv_s: Optional[float] = None
    hsv_v: Optional[float] = None

    hsl_h: Optional[float] = None
    hsl_s: Optional[float] = None
    hsl_l: Optional[float] = None

    focus: Optional[float] = None
    camera_metadata: Optional[dict] = None
    extract_metadata: Optional[dict] = None


class ExperimentResultModel(ORMBaseModel):
    id: uuid.UUID
    experiment_id: uuid.UUID
    value: float
    unit: str


class ExperimentModel(ORMBaseModel):
    id: uuid.UUID
    protocol_id: uuid.UUID
    user_id: uuid.UUID
    device_id: uuid.UUID

    experiment_name: str
    start_time: datetime
    status: ExperimentStatus
    comment: Optional[str] = None
    description: Optional[str] = None
    conclusion: Optional[str] = None
    error: Optional[str] = None

    valid: bool
    input_parameters: Optional[dict] = {}
    experiment_metadata: Optional[dict] = None

    image_extracts: List[ImageExtractModel] = []
    result: List[ExperimentResultModel] = []  # TODO: test
