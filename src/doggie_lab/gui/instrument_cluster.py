from doggie_lab.gui.gauge import SpeedometerGauge, TachometerGauge
from doggie_lab.gui.digital_display import (
    OdometerDisplay,
    CruiseControlDisplay,
    GearDisplay,
    StatusIndicator,
    DoorStatusDisplay,
    StartButton,
    DoorControlDisplay,
    ThrottleProgressBar,
    ButtonState
)
import dearpygui.dearpygui as dpg


class InstrumentCluster:
    """
    Car instrument cluster containing all gauges and digital displays.
    Encapsulates all internal components and exposes only update methods.
    """

    def __init__(
        self,
        parent_tag,
        button_callback,
        lock_doors,
        unlock_doors,
        toggle_airbag,
    ):
        """
        Initialize the instrument cluster with all gauges and displays.

        Args:
            parent_tag: Dear PyGui parent tag for the drawlist
        """
        self.parent_tag = parent_tag
        self.lock_doors = lock_doors
        self.unlock_doors = unlock_doors

        # Initialize gauges
        self._speedometer = SpeedometerGauge(
            parent_tag, center_x=120, center_y=150, radius=120
        )
        self._tachometer = TachometerGauge(
            parent_tag, center_x=630, center_y=150, radius=120
        )

        # Initialize digital displays (order: Gear, Cruise, Engine, ABS, Odometer, Doors)
        # self._gear_display = GearDisplay(parent_tag, center_x=375, center_y=50)
        self._cruise_control = CruiseControlDisplay(
            parent_tag,
            center_x=375,
            center_y=50,  # 120
        )
        self._airbag_warning = StatusIndicator(
            parent_tag,
            center_x=375,
            center_y=120,  # 170
            indicator_name="AIRBAG",
            inactive_color=(255, 165, 0, 255),
            active_color=(80, 80, 80, 255),
        )
        self._abs_indicator = StatusIndicator(
            parent_tag,
            center_x=375,
            center_y=170,  # 220
            indicator_name="ABS",
            inactive_color=(255, 0, 0, 255),
            active_color=(80, 80, 80, 255),
        )
        # self._odometer = OdometerDisplay(parent_tag, center_x=375, center_y=280)
        self._door_status = DoorStatusDisplay(
            parent_tag, center_x=375, center_y=280
        )  # 370

        self._start_button = StartButton(parent=parent_tag, pos=(20, 430))
        self._start_button.set_callback(button_callback)

        self._doors_controls = DoorControlDisplay(
            parent_tag, self.lock_doors, self.unlock_doors, [600, 470]
        )

        dpg.add_checkbox(
            label="Airbag enabled",
            default_value=True,
            callback=toggle_airbag,
            parent=parent_tag,
            pos=[580, 410],
        )

        self._throttle = ThrottleProgressBar(
            375, 400, parent_tag
        )

        dpg.add_separator(parent=parent_tag)

    def update_throttle(self, value: float) -> None:
        self._throttle.update_value(value if self._start_button.get_state() == ButtonState.ON else 0) 

    def set_button_state(self, state) -> None:
        self._start_button.set_state(state)

    def update_speed(self, speed):
        """Update speedometer value"""
        self._speedometer.update_value(speed)

    def update_rpm(self, rpm):
        """Update tachometer value"""
        self._tachometer.update_value(rpm)

    def update_gear(self, gear):
        """Update gear display"""
        self._gear_display.update_display(gear)

    def update_cruise_control(self, active, speed=None):
        """Update cruise control status"""
        self._cruise_control.update_cruise_status(active, speed)

    def update_airbag_warning(self, active):
        """Update engine warning light status"""
        self._airbag_warning.update_status(active)

    def update_abs_warning(self, active):
        """Update ABS warning light status"""
        self._abs_indicator.update_status(active)

    def update_odometer(self, value):
        """Update odometer display"""
        self._odometer.update_display(value)

    def update_door_status(self, door_states):
        """
        Update door status display

        Args:
            door_states: List of 4 booleans [FL, FR, RL, RR] where True = open, False = closed
        """
        self._door_status.update_door_status(door_states)

    def update_all(
        self,
        speed=0.0,
        rpm=0,
        gear="D",
        cruise_active=True,
        cruise_speed=None,
        airbag_warning=True,
        abs_warning=False,
        odometer_value=0.0,
        door_states=None,
    ):
        """
        Update all displays at once

        Args:
            speed: Speed in km/h
            rpm: Engine RPM
            gear: Current gear
            cruise_active: Whether cruise control is active
            cruise_speed: Cruise control target speed (if active)
            airbag_warning: Airbag warning light status
            abs_warning: ABS warning light status
            odometer_value: Odometer reading in km
            door_states: List of door states [FL, FR, RL, RR]
        """
        if door_states is None:
            door_states = [False, False, False, False]

        self.update_speed(speed)
        self.update_rpm(rpm)
        # self.update_gear(gear)
        self.update_cruise_control(
            cruise_active, cruise_speed if cruise_active else None
        )
        self.update_airbag_warning(airbag_warning)
        self.update_abs_warning(abs_warning)
        # self.update_odometer(odometer_value)
        self.update_door_status(door_states)
