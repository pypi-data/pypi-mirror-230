# Copyright (C) SG Papertronics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Job Heersink <j.g.heersink@sgpapertronics.com>, February 2023

import logging
from enum import Enum

from pydantic import BaseModel, validator
from typing import Optional, List, Tuple

from .generic import Point, MotorState, LightColor

logger = logging.getLogger(__name__)


class ZoomState(BaseModel):
    x_offset: int
    y_offset: int
    x_zoom: int
    y_zoom: int


class FocusMode(int, Enum):
    MANUAL = 0
    AUTO = 1
    # CONTINUOUS = 2


class FocusMetering(int, Enum):
    AUTO = 0
    WINDOWS = 1


class FocusRange(int, Enum):
    NORMAL = 0
    MACRO = 1
    FULL = 2


class FocusSpeed(int, Enum):
    NORMAL = 0
    FAST = 1


class CameraConfig(BaseModel):
    image_size: Point = Point(x=1280, y=1280)
    focus: Point = Point(x=1307, y=949)  # minimal measured focus 1266, 882. max measured focus 1347, 1016
    full: bool = False
    zoom: int = 1280
    awb: bool = False
    brightness: float = 0
    contrast: float = 1
    saturation: float = 1
    sharpness: float = 1
    exposure: Optional[int] = None
    af_mode: Optional[FocusMode] = None
    af_metering: FocusMetering = FocusMetering.AUTO
    af_range: FocusRange = FocusRange.MACRO
    af_speed: FocusSpeed = FocusSpeed.NORMAL
    af_windows: Optional[List[Tuple[int, int, int, int]]] = None  # TODO: how to do this
    analogue_gain: Optional[float] = None
    lens_position: Optional[float] = None

    class Config:
        validate_assignment = True
        use_enum_values = True

    def get_zoom_configuration(self) -> Optional[ZoomState]:
        if self.full:
            return None
        else:
            return ZoomState(x_offset=int(self.focus.x - self.zoom / 2),
                             y_offset=int(self.focus.y - self.zoom / 2),
                             x_zoom=self.zoom,
                             y_zoom=self.zoom)

    @validator('brightness')
    def validate_brightness(cls, v):
        if -1.0 <= v <= 1.0:
            return v
        else:
            raise ValueError(f"brightness {v} is not within [-1..1]")

    @validator('contrast')
    def validate_contrast(cls, v):
        if 0.0 <= v <= 32.0:
            return v
        else:
            raise ValueError(f"contrast {v} is not within [0..32]")

    @validator('saturation')
    def validate_saturation(cls, v):
        if 0.0 <= v <= 32.0:
            return v
        else:
            raise ValueError(f"saturation {v} is not within [0..32]")

    @validator('sharpness')
    def validate_sharpness(cls, v):
        if 0.0 <= v <= 16.0:
            return v
        else:
            raise ValueError(f"sharpness {v} is not within [0..16]")

    @validator('exposure')
    def validate_exposure(cls, v):
        if v is None or 26 <= v <= 220417486:
            return v
        else:
            raise ValueError(f"exposure {v} is not within [26..220417486] microseconds")

    @validator('analogue_gain')
    def validate_gain(cls, v):
        if v is None or 1 <= v <= 16:
            return v
        else:
            raise ValueError(f"exposure {v} is not within [1..16]")

    @validator('lens_position')
    def validate_lens_position(cls, v):
        if v is None or 0 <= v <= 32:
            return v
        else:
            raise ValueError(f"lens position {v} is not within [0..32]")


class Schedule(BaseModel):
    start: float
    light_color: Optional[LightColor] = None
    light_brightness: Optional[float] = None
    pump_on: Optional[bool] = None
    motor_state: Optional[MotorState] = None
    led_on: Optional[bool] = None
    capture_image: bool = False

    @validator('start')
    def validate_start(cls, v):
        if v >= 0:
            return v
        else:
            raise ValueError("start must be a positive number")

    @validator('light_color')
    def validate_light(cls, v):
        if v is not None:
            new_v = LightColor.read_tuple(v)
            new_v.validate()
            return new_v
        else:
            return None

    @validator('light_brightness')
    def validate_light_brightness(cls, v):
        if v is None:
            return None
        if 0 <= v <= 1:
            return v
        else:
            raise ValueError(f"the brightness of the light must be between 0 and 1")


class StationProtocol(BaseModel):
    light_color: LightColor = LightColor(0, 0, 0, 0)
    light_brightness: float = 1
    pump_on: bool = False
    motor_state: MotorState = MotorState.STOP
    timelapse_schedule: List[Schedule] = []
    lcd_messages: List[Tuple[int, str]] = []

    led_on: bool = False
    backlight_on: bool = True

    camera_configuration: CameraConfig = CameraConfig()

    class Config:
        validate_assignment = True

    def build_timelapse(self, interval: int, duration: int, flash: Optional[LightColor] = None, start_delay: int = 0): #TODO: test
        """
        Build a timelapse schedule based on the given interval and duration
        """
        nr_of_images = (duration // interval) + 1
        schedule_dict = {t.start: t for t in self.timelapse_schedule}

        if flash is not None:
            self.light_color = LightColor(0, 0, 0, 0)

        if flash is not None and start_delay < 1:
            raise Exception(f"flash was selected, but start delay is too short."
                            f"Start delay should be at least 1 second when flash is enabled")

        # ensure that there are no conflicts when building the timelapse
        for s in self.timelapse_schedule:
            if s.capture_image:
                raise Exception(f"protocol already has capture image tasks")
            if flash is not None and s.light_color is not None:
                raise Exception(f"flash was selected, but protocol already has light alterations.")

        for img_nr in range(nr_of_images):
            start_time = interval * img_nr + start_delay

            # if there is already a task at this time, add capture image to it. Otherwise, create a new task
            if start_time in schedule_dict:
                schedule_dict[start_time].capture_image = True
            else:
                self.timelapse_schedule.append(Schedule(start=start_time, capture_image=True))

            # add flash tasks to protocol steps
            if flash is not None:
                flash_start_time = start_time - 1
                flash_end_time = start_time + 1

                # if there is already a task at this time, add flash to it. Otherwise, create a new task
                if flash_start_time in schedule_dict:
                    schedule_dict[flash_start_time].light_color = flash
                else:
                    self.timelapse_schedule.append(Schedule(start=flash_start_time,
                                                            light_color=flash))

                # if there is already a task at this time, add flash to it. Otherwise, create a new task
                if flash_end_time in schedule_dict:
                    schedule_dict[flash_end_time].light_color = LightColor(0, 0, 0, 0)
                else:
                    self.timelapse_schedule.append(Schedule(start=flash_end_time,
                                                            light_color=LightColor(0, 0, 0, 0)))

        # trigger validation
        self.timelapse_schedule = self.timelapse_schedule

    @validator('light_color')
    def validate_light(cls, v):
        new_v = LightColor.read_tuple(v)
        new_v.validate()
        return new_v

    @validator('light_brightness')
    def validate_light_brightness(cls, v):
        if 0 <= v <= 1:
            return v
        else:
            raise ValueError(f"value must be between 0 and 1")

    @validator('timelapse_schedule')
    def validate_schedule(cls, v: List[Schedule]):
        v = sorted(v, key=lambda d: d.start)
        for i in range(1, len(v)):
            if v[i].start <= v[i - 1].start:
                raise ValueError(f"two or more scheduling items exist with the same start time. "
                                 f"Please ensure that the start of each scheduling item is unique")

        return v


class ProtocolProcessingDefinition(BaseModel):
    template_matching: bool
    mask_radius: float

    @validator('mask_radius')
    def validate_mask_radius(cls, v):
        if 0 <= v <= 1:
            return v
        else:
            raise ValueError(f"mask radius {v} is not within [0..1]")
