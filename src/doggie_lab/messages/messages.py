from abc import ABC, abstractmethod
from can import Message as CanMessage
from typing import Optional


class EcuMessage(ABC):
    @classmethod
    def from_can_msg(cls, msg: CanMessage) -> Optional["EcuMessage"]:
        if msg.arbitration_id != cls.get_id():
            return None

        return cls._from_bytes(msg.data)

    def to_can_msg(self) -> None:
        msg = CanMessage(arbitration_id=self.get_id(), data=self._to_bytes())
        return msg

    @classmethod
    @abstractmethod
    def _from_bytes(cls, data: bytes) -> Optional["EcuMessage"]:
        raise NotImplementedError

    @abstractmethod
    def _to_bytes(self) -> bytes:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_id() -> int:
        raise NotImplementedError


class EcuSubMessage(EcuMessage):
    @staticmethod
    @abstractmethod
    def get_sub_id() -> int:
        raise NotImplementedError

    @classmethod
    def from_can_msg(cls, msg: CanMessage) -> Optional["EcuMessage"]:
        if (
            msg.arbitration_id != cls.get_id()
            or msg.data == 0
            or msg.data[0] != cls.get_sub_id()
        ):
            return None

        return cls._from_bytes(msg.data[1:])

    def to_can_msg(self) -> None:
        data = self.get_sub_id().to_bytes(1, "big") + self._to_bytes()
        return CanMessage(
            arbitration_id=self.get_id(),
            data=data,
        )
