from doggie_lab.ecus.ecu_ui import Ecu
from doggie_lab.messages import (
    DoorsStatusMessage,
    DoorsControlMessage,
    SpeedStatusMessage,
)
import can
from doggie_lab.common.doors import DoorsStatus
import time
import threading


class DoorsEcu(Ecu):
    MAX_SPEED = 20

    def __init__(self, bus: can.BusABC, notifier: can.Notifier):
        super().__init__(bus, notifier, "Doors ECU")

        self._doors = DoorsStatus(True, True, True, True)
        self._speed = 0

        threading.Thread(target=self._report_loop, daemon=True).start()

    def _set_doors(self, msg: DoorsControlMessage) -> None:
        if self._speed < self.MAX_SPEED or msg.lock:
            if msg.fl:
                self._doors.fl = msg.lock

            if msg.fr:
                self._doors.fr = msg.lock

            if msg.rl:
                self._doors.rl = msg.lock

            if msg.rr:
                self._doors.rr = msg.lock

        self.send_msg(DoorsStatusMessage.from_status(self._doors).to_can_msg())

    def _report_loop(self):
        while True:
            time.sleep(0.1)
            self.send_msg(DoorsStatusMessage.from_status(self._doors).to_can_msg())

    def loop(self) -> None:
        while True:
            can_msg = self.get_msg()

            if (msg := DoorsControlMessage.from_can_msg(can_msg)) is not None:
                self._set_doors(msg)

            if (msg := SpeedStatusMessage.from_can_msg(can_msg)) is not None:
                self._speed = msg.speed
