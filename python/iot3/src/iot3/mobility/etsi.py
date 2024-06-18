# Software Name: IoT3 Mobility
# SPDX-FileCopyrightText: Copyright (c) 2024 Orange
# SPDX-License-Identifier: MIT
# Author: Yann E. MORIN <yann.morin@orange.com>

import datetime as _datetime
import math as _math


class ETSI:
    """Various ETSI-related constants

    Constants that help convert from SI units to ETSI scaled values.

    Note that the SI unit for angles is the radian, not the degree. However,
    when dealing with geo coordinates, it is more usual to use degrees to
    represent latitude and longitude. Hence, there are two scales for
    conversion: one, with no suffix, that converts from radians, and one,
    suffixed with _d, that converts from degrees.
    """

    # ETSI EPOCH, as a UNIX timestamp (int)
    EPOCH: int = int(
        _datetime.datetime.fromisoformat(
            "2004-01-01T00:00:00.000+00:00",
        ).timestamp()
    )

    # Length units
    METER: float = 1.0
    DECI_METER: float = METER / 10
    CENTI_METER: float = METER / 100
    MILLI_METER: float = METER / 1_000
    KILO_METER: float = METER * 1_000

    # Time units
    SECOND: float = 1.0
    MILLI_SECOND: float = SECOND / 1_000
    MICRO_SECOND: float = SECOND / 1_000_000
    NANO_SECOND: float = SECOND / 1_000_000_000

    # Speed units
    METER_PER_SECOND: float = METER / SECOND
    CENTI_METER_PER_SECOND: float = CENTI_METER / SECOND
    KILO_METER_PER_HOUR: float = KILO_METER / (3600.0 * SECOND)

    # Acceleration units
    METER_PER_SECOND_SECOND: float = METER / (SECOND * SECOND)
    DECI_METER_PER_SECOND_SECOND: float = DECI_METER / (SECOND * SECOND)

    # Angle units, converted from radians
    DEGREE: float = _math.radians(1.0)
    DECI_DEGREE: float = DEGREE / 10
    DECI_MICRO_DEGREE: float = DEGREE / 10_000_000

    # Angle units, converted from degrees
    DEGREE_d: float = 1.0
    DECI_DEGREE_d: float = DEGREE_d / 10
    DECI_MICRO_DEGREE_d: float = DEGREE_d / 10_000_000

    @staticmethod
    def generation_delta_time(timestamp: float) -> int:
        return si2etsi(timestamp - ETSI.EPOCH, ETSI.MILLI_SECOND, 0) % 65536

    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f"Class {cls.__name__} should not be instantiated")


def si2etsi(
    value: float | None,
    scale: float,
    undef: int,
    range: dict | None = None,
    out_of_range: int | None = None,
) -> int:
    """SI to ETSI unit conversions

    Each key in an ETSI object has its own scale, so there is no "ETSI unit"
    per-se, but a myriad of scales, each applicable to a specific key of a
    specific object. This function converts from an SI unit to an ETSI scale.

    :param value: the value in the SI unit, or None when the value is unknown
    :param scale: the ETSI scale of the key
    :param undef: the special ETSI-scaled value to use when the value is unknown
    :param validity_range: the lower and upper bounds of the value range as a
                  dict with keys "min" and "max", in ETSI scale; the bounds are
                  inclusive, but must not include undef and out_of_range.
    :param out_of_range: the special ETSI-scaled value to use when the value is
                         out of range
    :return: the special ETSI-scaled value 'undef' when the value is None, the
             special ETSI-scaled value 'out_of_range' if the value is out of
             range, or the value scaled to the ETSI scale otherwise

    For example:
        si2etsi(
            get_altitude_or_None(),
            ETSI.CENTI_METER,
            800001,
            {"min": 0, "max": 800000},
            800002,
        )

    Assuming that get_altitude_or_None() returns a number when the altitude is
    known, or None when it is unknown, the above code would return 800001 if the
    altitude is not known, 800002 if the altitude is lower than 0 or greater
    than 800000 (8000m), or the altitude as an integral number of centimeters.
    """
    if value is None:
        return undef
    etsi_value = int(round(value / scale))
    if range is not None:
        if etsi_value < range["min"]:
            etsi_value = out_of_range
        if etsi_value > range["max"]:
            etsi_value = out_of_range
    return etsi_value


def etsi2si(
    value: int,
    scale: float,
    undef: int,
    out_of_range: int | None = None,
) -> float | None:
    """ETSI to SI unit conversions

    Each key in an ETSI object has its own scale, so there is no "ETSI unit"
    per-se, but a myriad of scales, each applicable to a specific key of a
    specific object. This function converts from an ETSI scale to an SI unit.

    :param value: the value in an ETSI scale, or its special value when it
                  is unknown
    :param scale: the ETSI scale of the key
    :param undef: the special ETSI-scaled value to use when the value is unknown
    :param out_of_range: the special ETSI-scaled value to use when the value is
                         out of range
    :return: None if the value is the special ETSI-scaled value, the value in SI
             units otherwise

    For example:
        etsi2si(my_cam.altitude, ETSI.CENTI_METER, 800001)

    Assuming that my_cam.altitude contains a integer when the altitude
    is known, or the special value 800001 when it is unknown, the above
    code would return the altitude as a floating point numbers of meters,
    or None if the altitude is not known.
    """
    if value == undef:
        return None
    if out_of_range is not None and value == out_of_range:
        return None
    return float(value) * scale


def unix2etsi_time(
    value: float,
) -> int:
    """Convert UNIX timestamp to ETSI timestamp

    :param value: The UNIX timestamp, in seconds since the UNIX EPOCH, with
                  arbitrary sub-second precision
    :return: The ETSI timestamp, as the number of milliseconds elapsed since
             the ETSI EPOCH.

    If the value is a date before the ETSI EPOCH, the returned value is
    negative; it is left to the caller to decide whether that is usable
    in its case.
    """
    return si2etsi(value - ETSI.EPOCH, etsi.ETSI.MILLI_SECOND, 0)


def etsi2unix_time(
    value: int,
) -> float:
    """Convert ETSI timestamp to UNIX timestamp

    :param value: The ETSI timestamp, as the number of milliseconds elapsed
                  since the ETSI EPOCH.
    :return: The UNIX timestamp, in seconds since the UNIX EPOCH, with
             arbitrary sub-second precision (in oractice, down to millisecond
             precision).
    """
    return etsi2si(value, etsi.ETSI.MILLI_SECOND, 0) + ETSI.EPOCH
