#!/usr/bin/env python3
"""
 Various converters and utils

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
import cmath
import os
import warnings
from math import degrees, radians
from typing import Tuple

from pymap3d import enu2geodetic, geodetic2enu  # type: ignore

# get gps reference from environment variable
var = os.environ.get("GPS_REF")
if var is None:
    GPS_REF = (51.0, 6.0)
    warnings.warn(f"GPS_REF environment variable not set, using default {GPS_REF}")
else:
    GPS_REF = tuple(float(x) for x in var.split(","))  # type: ignore
    assert len(GPS_REF) == 2, f"invalid GPS_REF: {var}"


def set_gps_ref(lat: float, lon: float) -> None:
    """set gps reference point"""
    global GPS_REF  # pylint: disable=global-statement
    GPS_REF = (lat, lon)


def heading_to_theta(angle_deg: float) -> float:
    """convert gps heading to theta in radians"""
    h = -1j * cmath.rect(1, radians(angle_deg))
    return -cmath.phase(h)


def theta_to_heading(angle_rad: float) -> float:
    """convert theta in radians to gps heading"""
    h = -1j * cmath.rect(1, angle_rad)
    return degrees(-cmath.phase(h))  # type: ignore


def latlon_to_enu(latlon: Tuple[float, float]) -> Tuple[float, float]:
    x, y, _ = geodetic2enu(latlon[0], latlon[1], 0, GPS_REF[0], GPS_REF[1], 0)
    return x, y


def enu_to_latlon(xy: Tuple[float, float]) -> Tuple[float, float]:
    lat, lon, _ = enu2geodetic(xy[0], xy[1], 0, GPS_REF[0], GPS_REF[1], 0)
    return lat, lon
