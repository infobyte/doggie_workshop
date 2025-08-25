from doggie_lab.messages import EcuMessage
from doggie_lab import ids
from typing import Optional


class ImmoMessage(EcuMessage):
    @staticmethod
    def get_id() -> int:
        return ids.IMMO_ECU_ID


class KeyMessage(ImmoMessage):
    def __init__(self, key_inserted: bool) -> None:
        self.key_inserted = key_inserted

    @classmethod
    def _from_bytes(cls, data: bytes) -> Optional["KeyMessage"]:
        if len(data) <= 0:
            return None

        msg = cls(data[0] != 0)

        return msg

    def _to_bytes(self) -> bytes:
        data = self.key_inserted
        return data.to_bytes(1, "big")
