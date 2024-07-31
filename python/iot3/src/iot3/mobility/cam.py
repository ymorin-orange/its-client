# Software Name: IoT3 Mobility
# SPDX-FileCopyrightText: Copyright (c) 2023 Orange
# SPDX-License-Identifier: MIT
# Author: Yann E. MORIN <yann.morin@orange.com>

import datetime
import enum
import hashlib
import json
from . import etsi
from .gnss import GNSSReport


class CooperativeAwarenessMessage(etsi.Message):
    def __init__(
        self,
        *,
        uuid: str,
        station_type: StationType = etsi.Message.StationType.unknown,
        gnss_report: GNSSReport,
    ):
        """Create a basic Cooperative Awareness Message

        :param uuid: the UUID of this station
        :param station_type: The type of this station
        :param gnss_report: a GNSS report, coming from a GNSS device
        """
        self.message = dict(
            {
                "type": "cam",
                "origin": "self",
                "version": "1.1.3",
                "source_uuid": uuid,
                "timestamp": (
                    etsi.si2etsi(
                        datetime.datetime.now(datetime.timezone.utc).timestamp(),
                        etsi.ETSI.MILLI_SECOND,
                        0,
                    )
                ),
                "message": {
                    "protocol_version": 1,
                    "station_id": self.station_id(uuid),
                    "generation_delta_time": (
                        etsi.ETSI.generation_delta_time(gnss_report.timestamp)
                    ),
                    "basic_container": {
                        "station_type": station_type,
                        "reference_position": {
                            "latitude": etsi.si2etsi(
                                gnss_report.latitude,
                                etsi.ETSI.DECI_MICRO_DEGREE,
                                900000001,
                            ),
                            "longitude": etsi.si2etsi(
                                gnss_report.longitude,
                                etsi.ETSI.DECI_MICRO_DEGREE,
                                1800000001,
                            ),
                            "altitude": etsi.si2etsi(
                                gnss_report.altitude,
                                etsi.ETSI.CENTI_METER,
                                800001,
                            ),
                        },
                        "confidence": {
                            "position_confidence_ellipse": {
                                "semi_major_confidence": etsi.si2etsi(
                                    gnss_report.ellipse_major,
                                    etsi.ETSI.CENTI_METER,
                                    4095,
                                    {"min": 0, "max": 4093},
                                    4094,
                                ),
                                "semi_minor_confidence": etsi.si2etsi(
                                    gnss_report.ellipse_minor,
                                    etsi.ETSI.CENTI_METER,
                                    4095,
                                    {"min": 0, "max": 4093},
                                    4094,
                                ),
                                "semi_major_orientation": etsi.si2etsi(
                                    gnss_report.ellipse_orientation,
                                    etsi.ETSI.DECI_DEGREE,
                                    3601,
                                ),
                            },
                        },
                    },
                    "high_frequency_container": {
                        "heading": etsi.si2etsi(
                            gnss_report.track,
                            etsi.ETSI.DECI_DEGREE,
                            3601,
                        ),
                        "speed": etsi.si2etsi(
                            gnss_report.speed,
                            etsi.ETSI.CENTI_METER_PER_SECOND,
                            16383,
                        ),
                        "longitudinal_acceleration": etsi.si2etsi(
                            gnss_report.acceleration,
                            etsi.ETSI.DECI_METER_PER_SECOND_SECOND,
                            161,
                        ),
                    },
                },
            },
        )


# Shorthand
CAM = CooperativeAwarenessMessage
