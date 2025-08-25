from doggie_lab.ecus.ecu import Ecu
from doggie_lab.messages import (
    EngineStatusMessage,
    SpeedStatusMessage,
    RpmStatusMessage,
    KeyMessage,
    EngineControlMessage,
    CruiseControlMessage,
    AbsMessage,
    AbsStatusMessage,
    AirbagToggleMessage,
    AirbagStatusMessage
)
import can
import time
import threading
from enum import Enum
import random


RPM_BASE = 200


class EngineState(Enum):
    OFF = 0
    ON = 1


class Engine:
    def __init__(self) -> None:
        self.speed: int = 0
        self.rpm: int = RPM_BASE
        self.state = EngineState.OFF
        self.throttle = 0

        # Engine characteristics
        self.idle_rpm = 800
        self.max_rpm = 6000
        self.rpm_acceleration = 50  # RPM change per update cycle
        self.rpm_deceleration = 30

    def set_state(self, state: EngineState):
        self.state = state

        if state == EngineState.OFF:
            self.throttle = 0  # Reset throttle when turning off

    def set_throttle(self, throttle: int):
        """Set throttle position (0-100)"""
        if self.state == EngineState.ON:
            self.throttle = max(0, min(100, throttle))

        else:
            self.throttle = 0

    def update(self):
        """Called every 100ms to update engine state"""
        # if self.state == EngineState.OFF:
        #     self._update_off()

        # elif self.state == EngineState.ON:
        self._update_on()

    def _update_off(self):
        """Engine is off - RPM should decrease to 0"""
        self.rpm = max(0, self.rpm - self.rpm_deceleration * 2)
        self.speed = 0

    def _update_on(self):
        """Engine is on - respond to throttle input"""
        if self.state == EngineState.OFF:
            target_rpm = 0

        else:
            if self.throttle == 0:
                # No throttle - idle at idle_rpm
                target_rpm = self.idle_rpm
                # Add slight idle fluctuation
                target_rpm += random.randint(-10, 10)
            else:
                # Calculate target RPM based on throttle
                rpm_range = self.max_rpm - self.idle_rpm
                target_rpm = self.idle_rpm + int(rpm_range * self.throttle / 100)
                # Add some engine load simulation
                target_rpm += random.randint(-10, 10)

        # Smooth transition to target RPM
        if self.rpm < target_rpm:
            acceleration = self.rpm_acceleration * int(1 + self.throttle / 100)
            self.rpm += min(acceleration, target_rpm - self.rpm)
        elif self.rpm > target_rpm:
            deceleration = self.rpm_deceleration * int(1 + (100 - self.throttle) / 100)
            self.rpm -= min(deceleration, self.rpm - target_rpm)

        # Prevent over-revving and under-revving
        self.rpm = max(0, min(self.rpm, self.max_rpm))

        # Calculate speed based on RPM (simplified gear ratio)
        if self.rpm > self.idle_rpm:
            gear_ratio = 0.1  # Simplified gear ratio
            self.speed = int(
                self.speed * 0.8 + ((self.rpm - self.idle_rpm) * gear_ratio) * 0.2
            )
        else:
            self.speed = 0


class CentralEcu(Ecu):
    RPM_PHASE = 10

    def __init__(self, bus: can.BusABC, notifier: can.Notifier):
        super().__init__(bus, notifier, "Central ECU")

        self._engine = Engine()
        self._key_inserted = False
        self._abs_cnt = 0
        self._abs_error = False
        self._airbag_enabled = True

        threading.Thread(target=self._report_loop, daemon=True).start()

    def _start_engine(self):
        if not self._key_inserted:
            print("[Central ECU] Can't start engine, no key inserted")

        elif self._engine.state == EngineState.ON:
            print("[Central ECU] Can't start engine, engine running")

        else:
            print("[Central ECU] Starting engine")
            self._engine.set_state(EngineState.ON)
            self._abs_error = True
            self._airbag_enabled = False
            time.sleep(0.3)
            self._airbag_enabled = True
            time.sleep(0.5)
            self._abs_error = False
            self._abs_count = 0

    def _stop_engine(self):
        if self._engine.state == EngineState.OFF:
            print("[Central ECU] Can't stop engine, engine not running")

        else:
            self._engine.set_state(EngineState.OFF)

    def _report_status(self):
        msgs = [
            EngineStatusMessage(self._engine.state == EngineState.ON),
            RpmStatusMessage(self._engine.rpm),
            AbsStatusMessage(self._abs_error),
            AirbagStatusMessage(self._airbag_enabled),
            SpeedStatusMessage(self._engine.speed),
        ]

        for msg in msgs:
            self.send_msg(msg.to_can_msg())

    def _report_loop(self):
        while True:
            time.sleep(0.1)
            self._abs_cnt += 1
            self._emulate_engine()
            self._report_status()

            self._abs_error |= self._abs_cnt > 5


    def _emulate_engine(self) -> None:
        self._engine.update()

    def _cruise_control_handle(self, msg: CruiseControlMessage) -> None:
        if self._engine.state != EngineState.ON or not msg.enable:
            self._engine.throttle = 0

        else:
            self._engine.throttle = msg.throttle

    def loop(self):
        while True:
            can_msg = self.get_msg()

            if (msg := KeyMessage.from_can_msg(can_msg)) is not None:
                self._key_inserted = msg.key_inserted

            elif (msg := EngineControlMessage.from_can_msg(can_msg)) is not None:
                if msg.start_engine:
                    self._start_engine()
                else:
                    self._stop_engine()

                self._report_status()

            elif (msg := CruiseControlMessage.from_can_msg(can_msg)) is not None:
                self._cruise_control_handle(msg)

            elif (msg := AbsMessage.from_can_msg(can_msg)) is not None:
                self._abs_cnt = 0

            elif AirbagToggleMessage.from_can_msg(can_msg) is not None:
                self._airbag_enabled = not self._airbag_enabled

                self.send_msg(AirbagStatusMessage(self._airbag_enabled).to_can_msg())
