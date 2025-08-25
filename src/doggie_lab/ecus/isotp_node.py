import isotp
from can import BusABC, Notifier
from abc import ABC, abstractmethod


class IsotpNode(ABC):
    def __init__(self, bus: BusABC, notifier: Notifier):
        super().__init__()
        self.isotp_layer = isotp.NotifierBasedCanStack(
            bus,
            notifier,
            address=self.get_address(),
            params={"tx_padding": 0x00}
        )

    def start(self):
        self.isotp_layer.start()

    def stop(self):
        self.isotp_layer.stop()

    def get_isotp_msg(self) -> bytearray:
        msg = self.isotp_layer.recv(block=True)
        return msg

    def send_istop_msg(self, msg: bytearray):
        self.isotp_layer.send(msg)

    @abstractmethod
    def get_address(self) -> isotp.Address:
        """Return the address of the node."""
        pass
