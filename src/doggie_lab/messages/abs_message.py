from doggie_lab.messages import EcuMessage
from doggie_lab import ids
from typing import Optional


class AbsMessage(EcuMessage):
    @staticmethod
    def get_id() -> int:
        return ids.ABS_ECU_ID

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["AbsMessage"]:
        return AbsMessage

    def _to_bytes(self) -> bytes:
        return b""
