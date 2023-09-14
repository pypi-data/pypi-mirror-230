# Copyright (C) SG Papertronics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Job Heersink <j.g.heersink@sgpapertronics.com>, December 2022
import uuid

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from .database import ProtocolProcessingDefinition
from .station_protocol import StationProtocol


class ImageReference(BaseModel):
    order: int = 0
    bucket: str
    blob_name: str
    capture_time: datetime


class ExperimentError(BaseModel):
    error_message: str


class ExperimentAnalysesRequest(BaseModel):
    images: List[ImageReference] = []
    camera_metadata: List[dict] = {}


class ExperimentStartRequest(BaseModel):
    protocol_id: uuid.UUID
    name: str
    comment: Optional[str] = None
    description: Optional[str] = None
    conclusion: Optional[str] = None
    input_parameters: Optional[dict] = {}  # TODO: test
    experiment_metadata: Optional[dict] = None
    force_start: bool = False


class ExperimentEditRequest(BaseModel):
    valid: Optional[bool] = None
    comment: Optional[str] = None
    description: Optional[str] = None
    conclusion: Optional[str] = None
    experiment_name: Optional[str] = None


class ExperimentCancelCommand(BaseModel):
    experiment_id: uuid.UUID


class DeviceExperimentDefinition(BaseModel):
    experiment_name: str
    experiment_id: uuid.UUID
    protocol_name: str
    protocol: StationProtocol
    device_token: str


class SaveProtocolRequest(BaseModel):
    name: str
    test_type: Optional[str] = None
    device_definition: StationProtocol
    processing_definition: ProtocolProcessingDefinition


class ProtocolTestResponse(BaseModel):
    test_name: str
    test_parameters: Optional[dict] = None
