from doggie_lab.ecus.ecu import Ecu
from doggie_lab.ecus.isotp_node import IsotpNode
from can import BusABC, Notifier
import isotp


class VinEcu(Ecu, IsotpNode):
    flag = bytearray(b"flag{sarasaVIN123456789}")

    def __init__(self, bus: BusABC, notifier: Notifier):
        Ecu.__init__(self, bus, notifier, "Vin ECU")
        IsotpNode.__init__(self, bus, notifier)

    def get_address(self) -> isotp.Address:
        rx_id = 0x7DF  # Functional request, or use physical ID like 0x7E0
        tx_id = 0x7E8  # Response ID (usually ECU)
        return isotp.Address(isotp.AddressingMode.Normal_11bits, txid=tx_id, rxid=rx_id)

    def loop(self):
        msg = self.get_isotp_msg()
        # OBD or UDS
        if msg == bytes([0x09, 0x02]) or msg == bytes([0x22, 0xF1, 0x90]):
            self.send_istop_msg(self.flag)

    def start(self) -> None:
        Ecu.start(self)
        IsotpNode.start(self)

    def stop(self) -> None:
        Ecu.stop(self)
        IsotpNode.stop(self)
