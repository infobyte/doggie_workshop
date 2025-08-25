from doggie_lab.messages import EcuMessage
from doggie_lab import ids
from typing import Optional


class CruiseControlMessage(EcuMessage):
    @staticmethod
    def get_id() -> int:
        return ids.CRUISE_CONTROL_ECU_ID


class CruiseControlMessage(CruiseControlMessage):
    def __init__(self, enable: bool, throttle: int) -> None:
        self.enable = enable
        self.throttle = throttle

    @staticmethod
    def _trim_throttle(throttle: int) -> int:
        return min(100, max(0, throttle))

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["CruiseControlMessage"]:
        if len(data) <= 1:
            return None

        msg = cls(data[0] != 0, cls._trim_throttle(data[1]))

        return msg

    def _to_bytes(self) -> bytes:
        data = self._trim_throttle(self.throttle)
        return self.enable.to_bytes(1, "big") + data.to_bytes(1, "big")
