# Copyright (C) SG Papertronics - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Job Heersink <j.g.heersink@sgpapertronics.com>, December 2022

from enum import Enum

from typing import NamedTuple


class LightColor(NamedTuple):
    r: int
    g: int
    b: int
    w: int

    def validate(self):
        if not (0 <= self.r <= 255 and 0 <= self.g <= 255 and 0 <= self.b <= 255 and 0 <= self.w <= 255):
            raise ValueError(f"light color must be between 0 and 255")

    @staticmethod
    def read_tuple(v):
        if type(v) == tuple:
            return LightColor(*v)
        elif type(v) == LightColor:
            return v
        else:
            raise ValueError(f"{type(v)} is not LightColor or a tuple")


class Point(NamedTuple):
    x: int
    y: int


class MotorState(str, Enum):
    STOP = 'stop'
    DOWN = 'down'
    UP = 'up'
    COAST = 'coast'
