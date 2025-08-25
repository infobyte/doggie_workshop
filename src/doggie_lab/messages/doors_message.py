from doggie_lab.messages import EcuMessage
from doggie_lab.common.doors import DoorsStatus
from doggie_lab import ids
from typing import Optional


class DoorsStatusMessage(EcuMessage):
    @staticmethod
    def get_id() -> int:
        return ids.DOORS_ECU_ID

    def __init__(self, fr: bool, fl: bool, rr: bool, rl: bool) -> None:
        self.fr = fr
        self.fl = fl
        self.rr = rr
        self.rl = rl

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["DoorsStatusMessage"]:
        if len(data) <= 0:
            return None

        doors = data[0]
        msg = cls(doors & 8, doors & 4, doors & 2, doors & 1)

        return msg

    @staticmethod
    def from_status(state: DoorsStatus):
        return DoorsStatusMessage(state.fr, state.fl, state.rr, state.rl)

    def to_status(self) -> DoorsStatus:
        return DoorsStatus(self.fr, self.fl, self.rr, self.rl)

    def _to_bytes(self) -> bytes:
        data = self.fr << 3 | self.fl << 2 | self.rr << 1 | int(self.rl)
        return data.to_bytes(1, "big")
