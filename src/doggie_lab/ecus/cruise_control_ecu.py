from doggie_lab.ecus.ecu_ui import UiEcu
from doggie_lab.messages import SpeedStatusMessage, CruiseControlMessage
import dearpygui.dearpygui as dpg
import can
import time
import threading


class PIDController:
    """Simple PID controller for cruise control"""

    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.05):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain

        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()

        # Output limits
        self.output_min = -100.0
        self.output_max = 100.0

        # Anti-windup limits for integral term
        self.integral_min = -50.0
        self.integral_max = 50.0

    def update(self, setpoint: float, current_value: float) -> float:
        """
        Update PID controller and return control output

        Args:
            setpoint: Desired value (target speed)
            current_value: Current measured value (actual speed)

        Returns:
            Control output (throttle adjustment)
        """
        current_time = time.time()
        dt = current_time - self.last_time

        # Avoid division by zero
        if dt <= 0.0:
            dt = 0.01

        # Calculate error
        error = setpoint - current_value

        # Proportional term
        proportional = self.kp * error

        # Integral term
        self.integral += error * dt
        # Anti-windup: clamp integral term
        self.integral = max(self.integral_min, min(self.integral_max, self.integral))
        integral = self.ki * self.integral

        # Derivative term
        derivative = self.kd * (error - self.previous_error) / dt

        # Calculate output
        output = proportional + integral + derivative

        # Clamp output to limits
        output = max(self.output_min, min(self.output_max, output))

        # Update for next iteration
        self.previous_error = error
        self.last_time = current_time

        return output

    def reset(self):
        """Reset PID controller state"""
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()


class CruiseControlEcu(UiEcu):
    THRESHOLD = 10

    def __init__(self, bus: can.BusABC, notifier: can.Notifier):
        super().__init__(bus, notifier, "Cruise Control ECU")
        self._readed_speed = 0
        self._target_speed = 0
        self._enabled = True

        # PID Controller
        self.pid_controller = PIDController(
            kp=2.0,  # Proportional gain - how aggressively to respond to current error
            ki=0.5,  # Integral gain - how aggressively to respond to accumulated error
            kd=0.1,  # Derivative gain - how aggressively to respond to rate of change
        )

        self._init_ui()

        threading.Thread(target=self._control_loop, daemon=True).start()

    def _init_ui(self):
        dpg.add_slider_int(
            label="Speed",
            parent=self._window_tag,
            callback=self._set_speed_calback,
            default_value=0,
            min_value=0,
            max_value=300,
        )
        dpg.add_checkbox(
            label="Enabled",
            default_value=True,
            callback=self._enable_callback,
            parent=self._window_tag,
        )

    def _set_speed_calback(self, sender, app_data, user_data):
        self._target_speed = app_data

    def _enable_callback(self, sender, app_data, user_data):
        if not self._enabled and app_data:
            self.pid_controller.reset()

        self._enabled = app_data

    def _control(self) -> None:
        self.send_msg(
            CruiseControlMessage(
                self._enabled,
                int(self.pid_controller.update(self._target_speed, self._readed_speed)),
            ).to_can_msg()
        )

    def _control_loop(self) -> None:
        while True:
            time.sleep(0.2)

            self._control()

    def loop(self):
        while True:
            can_msg = self.get_msg()

            if (msg := SpeedStatusMessage.from_can_msg(can_msg)) is not None:
                self._readed_speed = msg.speed
