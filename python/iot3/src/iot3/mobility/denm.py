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


class DecentralizedEnvironmentalNotificationMessage(etsi.Message):
    class TerminationType(enum.IntEnum):
        # We need those values to *exactly* match those defined in the spec
        isCancellation = 0
        isNegation = 1

    class Cause(enum.IntEnum):
        # We need those values to *exactly* match those defined in the spec
        reserved = 0
        trafficCondition = 1
        accident = 2
        roadworks = 3
        adverseWeatherCondition_Adhesion = 6
        hazardousLocation_SurfaceCondition = 9
        hazardousLocation_ObstacleOnTheRoad = 10
        hazardousLocation_AnimalOnTheRoad = 11
        humanPresenceOnTheRoad = 12
        wrongWayDriving = 14
        rescueAndRecoveryWorkInProgress = 15
        adverseWeatherCondition_ExtremeWeatherCondition = 17
        adverseWeatherCondition_Visibility = 18
        adverseWeatherCondition_Precipitation = 19
        slowVehicle = 26
        dangerousEndOfQueue = 27
        vehicleBreakdown = 91
        postCrash = 92
        humanProblem = 93
        stationaryVehicle = 94
        emergencyVehicleApproaching = 95
        hazardousLocation_DangerousCurve = 96
        collisionRisk = 97
        signalViolation = 98
        dangerousSituation = 99

    _seq_nums = dict()

    def __init__(
        self,
        *,
        uuid: str,
        gnss_report: GNSSReport,
        detect_time: float | None = None,
        cause: Cause = Cause.dangerousSituation,
        validity_duration: int | float | None = None,
        termination: TerminationType | None = None,
    ):
        """Create a basic Decentralized Environmental Notification Message

        :param uuid: the UUID of this station
        :param gnss_report: a GNSS report, coming from a GNSS device
        :param detect_time: time of detection of the event
        :param cause: cause of the event
        :param validity_duration: duration the event is valid for
        :param termination: the type of termination for this event
        """
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if detect_time is None:
            detect_time = now

        self._message = dict(
            {
                "type": "cam",
                "origin": "self",
                "version": "1.1.3",
                "source_uuid": uuid,
                "timestamp": etsi.si2etsi(now, etsi.ETSI.MILLI_SECOND, 0),
                "message": {
                    "protocol_version": 1,
                    "station_id": self.station_id(uuid),
                    "management_container": {
                        "action_id": {
                            "originating_station_id": seld.station_id(uuid),
                            "sequence_number": self._get_seq_num(uuid),
                        },
                        "detection_time": etsi.unix2etsi_time(detect_time),
                        "reference_time": etsi.unix2etsi_time(now),
                        "event_position": {
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
                    },
                    "situation_container": {
                        "event_type": {
                            "cause": cause,
                        },
                    },
                },
            },
        )
        if termination is not None:
            self._message["message"]["management_container"][
                "termination"
            ] = termination
        if validity_duration is not None:
            self._message["message"]["management_container"][
                "validity_duration"
            ] = validity_duration

    @classmethod
    def _get_seq_num(
        cls,
        uuid: str,
    ) -> int:
        try:
            cls._seq_nums[uuid] += 1
        except KeyError:
            cls._seq_nums[uuid] = 0
        return cls._seq_nums[uuid]


# Shorthand
DENM = DecentralizedEnvironmentalNotificationMessage
