from doggie_lab.messages.messages import EcuSubMessage
from doggie_lab import ids
from typing import Optional
import struct


class CentralEcuMessage(EcuSubMessage):
    @staticmethod
    def get_id() -> int:
        return ids.CENTRAL_ECU_ID


class EngineStatusMessage(CentralEcuMessage):
    @staticmethod
    def get_sub_id() -> int:
        return 1

    def __init__(self, engine_on: bool) -> None:
        self.engine_on = engine_on

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["EngineStatusMessage"]:
        if len(data) < 1:
            return None

        msg = cls(data[0] != 0)

        return msg

    def _to_bytes(self) -> bytes:
        data = self.engine_on > 0
        return data.to_bytes(1, "big")


class SpeedStatusMessage(CentralEcuMessage):
    @staticmethod
    def get_sub_id() -> int:
        return 2

    def __init__(self, speed: int) -> None:
        self.speed = speed

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["SpeedStatusMessage"]:
        if len(data) < 2:
            return None

        msg = cls(struct.unpack(">H", data[:2])[0])

        return msg

    def _to_bytes(self) -> bytes:
        return self.speed.to_bytes(2, "big")


class RpmStatusMessage(CentralEcuMessage):
    @staticmethod
    def get_sub_id() -> int:
        return 3

    def __init__(self, rpm: int) -> None:
        self.rpm = rpm

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["RpmStatusMessage"]:
        if len(data) < 2:
            return None

        msg = cls(struct.unpack(">H", data[:2])[0])

        return msg

    def _to_bytes(self) -> bytes:
        return self.rpm.to_bytes(2, "big")


class AbsStatusMessage(CentralEcuMessage):
    @staticmethod
    def get_sub_id() -> int:
        return 4

    def __init__(self, failed: bool) -> None:
        self.failed = failed

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["EngineStatusMessage"]:
        if len(data) < 1:
            return None

        msg = cls(data[0] != 0)

        return msg

    def _to_bytes(self) -> bytes:
        return self.failed.to_bytes(1, "big")


class AirbagStatusMessage(CentralEcuMessage):
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    @staticmethod
    def get_sub_id() -> int:
        return 5

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["AirbagStatusMessage"]:
        if len(data) <= 0:
            return None

        msg = cls(data[0] != 0)

        return msg

    def _to_bytes(self) -> bytes:
        data = self.enabled
        return data.to_bytes(1, "big")
