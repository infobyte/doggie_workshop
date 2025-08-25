from doggie_lab.ecus.ecu_ui import UiEcu
from doggie_lab.gui.instrument_cluster import InstrumentCluster
from doggie_lab.gui.digital_display import ButtonState, StartButton
from doggie_lab.messages import (
    SpeedStatusMessage,
    RpmStatusMessage,
    EngineStatusMessage,
    EngineControlMessage,
    DoorsStatusMessage,
    DoorsControlMessage,
    AbsStatusMessage,
    AirbagToggleMessage,
    AirbagStatusMessage,
    CruiseControlMessage,
)
from enum import Enum
import can


class MsgCmd(Enum):
    SPEED = 0x00
    RPM = 0x01


class InstrumentsClusterEcu(UiEcu):
    """
    ECU_ISOTP_ID:
        RX: 0x7E1
        TX: 0x7E9
    """

    def __init__(self, bus: can.BusABC, notifier: can.Notifier):
        super().__init__(bus, notifier, "Instrument Cluster ECU")

        self._window_thread = None
        self._instruments = InstrumentCluster(
            self._window_tag,
            self._start_button_callback,
            self._lock_doors_callback,
            self._unlock_doors_callback,
            self._toggle_airbag_callback,
        )

        self._instruments.update_all()

    def _toggle_airbag_callback(self) -> None:
        self.send_msg(AirbagToggleMessage().to_can_msg())

    def _lock_doors_callback(self) -> None:
        self.send_msg(DoorsControlMessage(True, True, True, True, True).to_can_msg())

    def _unlock_doors_callback(self) -> None:
        self.send_msg(DoorsControlMessage(False, True, True, True, True).to_can_msg())

    def _start_button_callback(self, button: StartButton, state: ButtonState) -> None:
        if state == ButtonState.ON:
            self.send_msg(EngineControlMessage(False).to_can_msg())

        elif state == ButtonState.OFF:
            self._instruments.set_button_state(ButtonState.IGNITION)
            self.send_msg(EngineControlMessage(True).to_can_msg())

        elif state == ButtonState.IGNITION:
            # self._intruments.set_button_state(ButtonState.OFF)
            pass

    def loop(self):
        while True:
            can_msg = self.get_msg()

            if (msg := SpeedStatusMessage.from_can_msg(can_msg)) is not None:
                self._instruments.update_speed(msg.speed)

            elif (msg := RpmStatusMessage.from_can_msg(can_msg)) is not None:
                self._instruments.update_rpm(msg.rpm)

            elif (msg := EngineStatusMessage.from_can_msg(can_msg)) is not None:
                if msg.engine_on:
                    self._instruments.set_button_state(ButtonState.ON)
                else:
                    self._instruments.set_button_state(ButtonState.OFF)

            elif (msg := DoorsStatusMessage.from_can_msg(can_msg)) is not None:
                self._instruments.update_door_status([msg.fl, msg.fr, msg.rl, msg.rr])

            elif (msg := AbsStatusMessage.from_can_msg(can_msg)) is not None:
                self._instruments.update_abs_warning(not msg.failed)

            elif (msg := AirbagStatusMessage.from_can_msg(can_msg)) is not None:
                self._instruments.update_airbag_warning(msg.enabled)

            elif (msg := CruiseControlMessage.from_can_msg(can_msg)) is not None:
                self._instruments.update_cruise_control(msg.enable, None)
                self._instruments.update_throttle(
                    msg.throttle / 100 if msg.enable else 0.0
                )
