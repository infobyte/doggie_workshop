from doggie_lab.ecus.ecu_ui import Ecu
from doggie_lab.messages import AbsMessage
import can
import time


class ImmoEcu(Ecu):
    def __init__(self, bus: can.BusABC, notifier: can.Notifier):
        super().__init__(bus, notifier, "ABS ECU")

    def loop(self):
        while True:
            time.sleep(0.5)
            self.send_msg(AbsMessage().to_can_msg())
