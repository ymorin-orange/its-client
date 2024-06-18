# Software Name: IoT3 Mobility
# SPDX-FileCopyrightText: Copyright (c) 2024 Orange
# SPDX-License-Identifier: MIT
# Author: Yann E. MORIN <yann.morin@orange.com>

import dataclasses as _dataclasses
import math as _math


@_dataclasses.dataclass(frozen=True)
class GNSSReport:
    """A GNSS report.

    All values in SI units (except where noted), with arbitrary precision.
    Any value (but timestamp) may be None, when unknown or unavailable.

    When a field exist in both radians and degrees, only one may be set when
    instantiating the class, not both. The other will automatically be set.

    :param timestamp: UNIX timestamp this object was created at, with
                      arbitrary sub-second precision
    :param time: Time as sent by the GNSS service, with arbitrary sub-second
                 precision
    :param latitude: Latitude
    :param longitude: Longitude
    :param latitude_d: Latitude in degrees
    :param longitude_d: Longitude in degrees
    :param altitude: Altitude
    :param speed: Speed over ground (i.e. without vertical component)
    :param acceleration: Acceleration
    :param track: Orientation from true North (geographic North, not
                  magnetic North!)
    :param ellipse_major: Semi-major axis for error ellipse
    :param ellipse_minor: Semi-minor axis for error ellipse
    :param ellipse_orientation: Orientation of semi-major axis of error
                                ellipse, from true north
    :param ellipse_orientation_d: Orientation of semi-major axis of error
                                  ellipse, from true north, in degrees
    :param altitude_error: Error in altitude measurement.
    :param true_heading: True headings (may or may not be equal to track,
                         above)
    :param true_heading_d: True headings (may or may not be equal to track,
                           above), in degrees
    :param magnetic_heading: Magnetic heading
    :param magnetic_heading_d: Magnetic heading, in degrees
    """

    timestamp: float
    time: float | None = None
    latitude: float | None = None
    latitude_d: float | None = None
    longitude: float | None = None
    longitude_d: float | None = None
    altitude: float | None = None
    speed: float | None = None
    acceleration: float | None = None
    track: float | None = None
    ellipse_major: float | None = None
    ellipse_minor: float | None = None
    ellipse_orientation: float | None = None
    ellipse_orientation_d: float | None = None
    altitude_error: float | None = None
    true_heading: float | None = None
    magnetic_heading: float | None = None
    true_heading_d: float | None = None
    magnetic_heading_d: float | None = None

    def __post_init__(self):
        fields = {
            # min_inc, max_inc: inclusive boundaries
            # min_exc, max_exc: exclusibe boundaries
            "latitude": {
                "min_inc": _math.radians(-90.0),
                "max_inc": _math.radians(90.0),
            },
            "longitude": {
                "min_exc": _math.radians(-180.0),
                "max_inc": _math.radians(180.0),
            },
            "ellipse_orientation": {
                "min_exc": _math.radians(-180.0),
                "max_exc": _math.radians(180.0),
            },
            "true_heading": {
                "min_exc": _math.radians(-180.0),
                "max_exc": _math.radians(360.0),
            },
            "magnetic_heading": {
                "min_exc": _math.radians(-180.0),
                "max_inc": _math.radians(180.0),
            },
        }

        def _range(f, as_degrees=False):
            min_rng = ""
            if "min_inc" in fields[f]:
                min_rng += f"[{_math.degrees(fields[f]['min_inc']) if as_degrees else fields[f]['min_inc']}"
            elif "min_exc" in fields[f]:
                min_rng += f"]{_math.degrees(fields[f]['min_exc']) if as_degrees else fields[f]['min_exc']}"
            max_rng = ""
            if "max_inc" in fields[f]:
                max_rng += f"{_math.degrees(fields[f]['max_inc']) if as_degrees else fields[f]['max_inc']}]"
            elif "max_exc" in fields[f]:
                max_rng += f"{_math.degrees(fields[f]['max_exc']) if as_degrees else fields[f]['max_exc']}["
            if min_rng and max_rng:
                rng = f"{min_rng}, {max_rng}"
            elif min_rng:
                rng = f"{min_rng}, ...]"
            elif max_rng:
                rng = f"[..., {max_rng}"
            return rng

        def _validate(f, v, f_d=None, v_d=None):
            if "min_inc" in fields[f] and v < fields[f]["min_inc"]:
                raise AttributeError(
                    f"{f_d or f} {v_d if f_d else v} is out of range {_range(f, f_d)}"
                )
            if "min_exc" in fields[f] and v <= fields[f]["min_exc"]:
                raise AttributeError(
                    f"{f_d or f} {v_d if f_d else v} is out of range {_range(f, f_d)}"
                )
            if "max_inc" in fields[f] and v > fields[f]["max_inc"]:
                raise AttributeError(
                    f"{f_d or f} {v_d if f_d else v} is out of range {_range(f, f_d)}"
                )
            if "max_exc" in fields[f] and v >= fields[f]["max_exc"]:
                raise AttributeError(
                    f"{f_d or f} {v_d if f_d else v} is out of range {_range(f, f_d)}"
                )

        # For each field, validate that either are set, or none, but not both,
        # and that they are in range. If one is set, convert to the other.
        for f in fields:
            rad = getattr(self, f)
            deg = getattr(self, f"{f}_d")
            if rad is not None and deg is not None:
                raise AttributeError(f"Only one of {f} or {f}_d can be set")
            if rad is not None:
                _validate(f, rad)
                object.__setattr__(self, f"{f}_d", _math.degrees(rad))
            elif deg is not None:
                rad = _math.radians(deg)
                _validate(f, rad, f"{f}_d", deg)
                object.__setattr__(self, f"{f}", rad)
