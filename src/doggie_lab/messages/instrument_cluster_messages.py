from doggie_lab.messages import EcuSubMessage
from doggie_lab import ids
from typing import Optional


class InstrumentClusterMessage(EcuSubMessage):
    @staticmethod
    def get_id() -> int:
        return ids.INSTRUMENT_CLUSTER_ID


class EngineControlMessage(InstrumentClusterMessage):
    @staticmethod
    def get_sub_id() -> int:
        return 0

    def __init__(self, start_engine: bool) -> None:
        self.start_engine = start_engine

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["EngineControlMessage"]:
        if len(data) < 1:
            return None

        msg = cls(data[0] != 0)

        return msg

    def _to_bytes(self) -> bytes:
        data = self.start_engine > 0
        return data.to_bytes(1, "big")


class DoorsControlMessage(InstrumentClusterMessage):
    @staticmethod
    def get_sub_id() -> int:
        return 1

    def __init__(self, lock: bool, fr: bool, fl: bool, rr: bool, rl: bool) -> None:
        self.fr = fr
        self.fl = fl
        self.rr = rr
        self.rl = rl
        self.lock = lock

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["DoorsControlMessage"]:
        if len(data) <= 1:
            return None

        lock = data[0] != 0

        doors = data[1]
        msg = cls(lock, doors & 8, doors & 4, doors & 2, doors & 1)

        return msg

    def _to_bytes(self) -> bytes:
        data = self.fr << 3 | self.fl << 2 | self.rr << 1 | int(self.rl)
        return self.lock.to_bytes(1, "big") + data.to_bytes(1, "big")


class AirbagToggleMessage(InstrumentClusterMessage):
    @staticmethod
    def get_sub_id() -> int:
        return 2

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["AirbagToggleMessage"]:
        return cls()

    def _to_bytes(self) -> bytes:
        return b""
