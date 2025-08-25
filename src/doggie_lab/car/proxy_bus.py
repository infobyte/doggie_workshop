from can import BusABC, Message
from typing import Optional


class ProxyBus(BusABC):
    def __init__(self, tx_bus: BusABC, rx_bus: BusABC):
        self._tx_bus = tx_bus
        self._rx_bus = rx_bus

    def recv(self, timeout: Optional[float] = None) -> Optional[Message]:
        return self._rx_bus.recv(timeout)

    def send(self, msg: Message, timeout: Optional[float] = None) -> None:
        self._tx_bus.send(msg, timeout)
