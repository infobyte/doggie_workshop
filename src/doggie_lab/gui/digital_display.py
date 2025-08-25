import dearpygui.dearpygui as dpg
from enum import Enum


class DigitalDisplay:
    """Digital display class for text-based dashboard information"""

    def __init__(
        self,
        parent_tag,
        center_x,
        center_y,
        width=200,
        height=50,
        text_color=(255, 255, 255, 255),
        background_color=(0, 0, 0, 255),
        border_color=(100, 100, 100, 255),
        font_size=16,
        label="",
        label_color=(150, 150, 150, 255),
        label_size=12,
        text_format="{}",
        units="",
        justify="center",
    ):
        """
        Digital display for dashboard information

        Args:
            parent_tag: Dear PyGui parent tag for drawing
            center_x, center_y: Center position of the display
            width, height: Dimensions of the display
            text_color: Color of the main text
            background_color: Background color of the display
            border_color: Border color
            font_size: Size of the main text
            label: Label text to show above the display
            label_color: Color of the label text
            label_size: Size of the label text
            text_format: Format string for the value (e.g., "{:.1f}", "{:06d}")
            units: Units to display after the value
            justify: Text justification ("left", "center", "right")
        """
        self.parent_tag = parent_tag
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        # Calculate top-left corner from center
        self.x = center_x - width // 2
        self.y = center_y - height // 2
        self.text_color = text_color
        self.background_color = background_color
        self.border_color = border_color
        self.font_size = font_size
        self.label = label
        self.label_color = label_color
        self.label_size = label_size
        self.text_format = text_format
        self.units = units
        self.justify = justify

        # Track elements for updates
        self.display_id = f"digital_{center_x}_{center_y}"
        self.background_tag = f"{self.display_id}_bg"
        self.border_tag = f"{self.display_id}_border"
        self.text_tag = f"{self.display_id}_text"
        self.label_tag = f"{self.display_id}_label"
        self.static_drawn = False

    def draw_static_elements(self):
        """Draw the static elements (background, border, label)"""
        if self.static_drawn:
            return

        # Draw background
        dpg.draw_rectangle(
            (self.x, self.y),
            (self.x + self.width, self.y + self.height),
            color=self.background_color,
            fill=self.background_color,
            parent=self.parent_tag,
            tag=self.background_tag,
        )

        # Draw border
        dpg.draw_rectangle(
            (self.x, self.y),
            (self.x + self.width, self.y + self.height),
            color=self.border_color,
            thickness=2,
            parent=self.parent_tag,
            tag=self.border_tag,
        )

        # Draw label if provided
        if self.label:
            label_x = (
                self.x + (self.width // 2) - (len(self.label) * self.label_size // 4)
            )
            label_y = self.y - self.label_size - 5
            dpg.draw_text(
                (label_x, label_y),
                self.label,
                size=self.label_size,
                color=self.label_color,
                parent=self.parent_tag,
                tag=self.label_tag,
            )

        self.static_drawn = True

    def update_display(self, value):
        """Update the display with a new value"""
        # Ensure static elements are drawn
        self.draw_static_elements()

        # Delete existing text
        if dpg.does_item_exist(self.text_tag):
            dpg.delete_item(self.text_tag)

        # Format the value
        if isinstance(value, (int, float)):
            display_text = self.text_format.format(value)
        else:
            display_text = str(value)

        if self.units:
            display_text += f" {self.units}"

        # Calculate text position based on justification
        text_width = len(display_text) * (self.font_size * 0.6)  # Rough estimation
        if self.justify == "center":
            text_x = self.x + (self.width - text_width) // 2
        elif self.justify == "right":
            text_x = self.x + self.width - text_width - 10
        else:  # left
            text_x = self.x + 10

        text_y = self.y + (self.height - self.font_size) // 2

        # Draw the text
        dpg.draw_text(
            (text_x, text_y),
            display_text,
            size=self.font_size,
            color=self.text_color,
            parent=self.parent_tag,
            tag=self.text_tag,
        )

    def draw(self, value):
        """Draw the complete display"""
        self.update_display(value)


class OdometerDisplay(DigitalDisplay):
    """Preconfigured odometer display"""

    def __init__(self, parent_tag, center_x, center_y):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            width=180,
            height=40,
            text_color=(0, 255, 0, 255),  # Green
            background_color=(0, 0, 0, 255),
            border_color=(100, 100, 100, 255),
            font_size=18,
            label="ODOMETER",
            text_format="{:.1f}",
            units="km",
            justify="center",
        )


class CruiseControlDisplay(DigitalDisplay):
    """Preconfigured cruise control status display"""

    def __init__(self, parent_tag, center_x, center_y):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            width=120,
            height=30,
            text_color=(255, 255, 0, 255),  # Yellow
            background_color=(0, 0, 0, 255),
            border_color=(100, 100, 100, 255),
            font_size=14,
            label="CRUISE",
            text_format="{}",
            justify="center",
        )

    def update_cruise_status(self, active, speed=None):
        """Update cruise control status

        Args:
            active: Boolean indicating if cruise control is active
            speed: Target speed if active, None if inactive
        """
        if active and speed is not None:
            self.update_display(f"SET {speed:.0f}")
        elif active:
            self.update_display("ON")
        else:
            self.update_display("OFF")


class GearDisplay(DigitalDisplay):
    """Preconfigured gear indicator display"""

    def __init__(self, parent_tag, center_x, center_y):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            width=80,
            height=60,
            text_color=(255, 255, 255, 255),
            background_color=(0, 0, 0, 255),
            border_color=(100, 100, 100, 255),
            font_size=36,
            label="GEAR",
            text_format="{}",
            justify="center",
        )


class StatusIndicator(DigitalDisplay):
    """Generic status indicator for various warning lights"""

    def __init__(
        self,
        parent_tag,
        center_x,
        center_y,
        indicator_name,
        active_color=(255, 0, 0, 255),
        inactive_color=(50, 50, 50, 255),
    ):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            width=100,
            height=25,
            text_color=active_color,
            background_color=(0, 0, 0, 255),
            border_color=(100, 100, 100, 255),
            font_size=12,
            label=indicator_name,
            text_format="{}",
            justify="center",
        )
        self.active_color = active_color
        self.inactive_color = inactive_color

    def update_status(self, active):
        """Update the status indicator

        Args:
            active: Boolean indicating if the status is active
        """
        self.text_color = self.active_color if active else self.inactive_color
        status_text = "ON" if active else "OFF"
        self.update_display(status_text)


class DoorStatusDisplay(DigitalDisplay):
    """Door status display showing all doors' open/closed state"""

    def __init__(self, parent_tag, center_x, center_y):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            width=160,
            height=80,
            text_color=(255, 255, 255, 255),
            background_color=(0, 0, 0, 255),
            border_color=(100, 100, 100, 255),
            font_size=12,
            label="DOORS",
            text_format="{}",
            justify="left",
        )
        self.door_labels = [
            "FL",
            "FR",
            "RL",
            "RR",
        ]  # Front Left, Front Right, Rear Left, Rear Right
        self.open_color = (255, 0, 0, 255)  # Red for open
        self.closed_color = (0, 255, 0, 255)  # Green for closed

        # Individual door text tags
        self.door_text_tags = [f"{self.display_id}_door_{i}" for i in range(4)]

    def update_door_status(self, door_states):
        """Update door status display

        Args:
            door_states: List of 4 booleans [FL, FR, RL, RR] where True = closed, False = open
        """
        # Ensure static elements are drawn
        self.draw_static_elements()

        # Delete existing door text elements
        for tag in self.door_text_tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)

        # Draw each door status
        start_x = self.x + 10
        start_y = self.y + 15

        # Draw doors in 2x2 grid layout
        positions = [
            (start_x, start_y),  # FL - top left
            (start_x + 70, start_y),  # FR - top right
            (start_x, start_y + 25),  # RL - bottom left
            (start_x + 70, start_y + 25),  # RR - bottom right
        ]

        for i, (door_closed, pos, label) in enumerate(
            zip(door_states, positions, self.door_labels)
        ):
            color = self.closed_color if door_closed else self.open_color
            status = "CLOSED" if door_closed else "OPEN"
            text = f"{label}: {status}"

            dpg.draw_text(
                pos,
                text,
                size=self.font_size,
                color=color,
                parent=self.parent_tag,
                tag=self.door_text_tags[i],
            )


class ThrottleProgressBar:
    def __init__(self, center_x: float, center_y: float, parent: int | str):
        """
        Initialize a throttle progress bar with specified center position and parent.

        Args:
            center_x (float): X-coordinate of the progress bar's center
            center_y (float): Y-coordinate of the progress bar's center
            parent (int | str): Parent DearPyGui tag
        """
        self.width = 200
        self.height = 60
        self.tag = dpg.generate_uuid()

        # Calculate top-left corner from center point
        pos_x = center_x - (self.width / 2)
        pos_y = center_y - (self.height / 2)

        # Create progress bar
        with dpg.group(parent=parent):
            self.progress_bar = dpg.add_progress_bar(
                default_value=0.0,
                width=self.width,
                height=self.height,
                pos=[pos_x, pos_y],
                overlay="Throttle: 0%",
            )

            # Add styling compatible with older DearPyGui versions
            with dpg.theme() as self.theme:
                with dpg.theme_component(dpg.mvProgressBar):
                    # Use mvThemeCol_ProgressBar instead of mvThemeCol_BarFill
                    dpg.add_theme_color(
                        dpg.mvProgressBar,
                        [0, 255, 0, 255],  # Green fill
                        category=dpg.mvThemeCat_Core,
                    )
                    dpg.add_theme_color(
                        dpg.mvThemeCol_FrameBg,
                        [50, 50, 50, 255],  # Dark grey background
                        category=dpg.mvThemeCat_Core,
                    )

            dpg.bind_item_theme(self.progress_bar, self.theme)

    def update_value(self, value: float) -> None:
        """
        Update the throttle progress bar value.

        Args:
            value (float): Value between 0.0 and 1.0 representing throttle percentage
        """
        # Clamp value between 0.0 and 1.0
        clamped_value = max(0.0, min(1.0, value))
        dpg.set_value(self.progress_bar, clamped_value)
        dpg.configure_item(
            self.progress_bar, overlay=f"Throttle: {int(clamped_value * 100)}%"
        )


class ButtonState(Enum):
    OFF = "OFF"
    IGNITION = "IGNITION"
    ON = "ON"


class StartButton:
    def __init__(self, parent=None, tag=None, pos=(0, 0), size=(120, 120)):
        self.state = ButtonState.OFF
        self.tag = tag or dpg.generate_uuid()
        self.parent = parent
        self.pos = pos
        self.size = size
        self.callback = None

        # State colors
        self.state_colors = {
            ButtonState.OFF: (100, 100, 100, 255),  # Gray
            ButtonState.IGNITION: (255, 165, 0, 255),  # Orange
            ButtonState.ON: (0, 255, 0, 255),  # Green
        }

        # Create the button
        self._create_button()

    def _create_button(self):
        """Create the visual button component."""
        with dpg.group(parent=self.parent, tag=f"{self.tag}_group"):
            # Create button with initial styling
            self.button_tag = dpg.add_button(
                label=self.state.value,
                callback=self._on_click,
                pos=self.pos,
                width=self.size[0],
                height=self.size[1],
                tag=f"{self.tag}_button",
            )

            # Create all themes at initialization to avoid runtime issues
            self._create_themes()

            # Apply initial color theme
            self._update_appearance()

    def _create_themes(self):
        """Create all themes during initialization."""
        for state in ButtonState:
            color = self.state_colors[state]
            theme_tag = f"{self.tag}_theme_{state.value}"

            with dpg.theme(tag=theme_tag):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(
                        dpg.mvThemeCol_Button, color, category=dpg.mvThemeCat_Core
                    )
                    dpg.add_theme_color(
                        dpg.mvThemeCol_ButtonHovered,
                        (
                            min(255, color[0] + 30),
                            min(255, color[1] + 30),
                            min(255, color[2] + 30),
                            255,
                        ),
                        category=dpg.mvThemeCat_Core,
                    )
                    dpg.add_theme_color(
                        dpg.mvThemeCol_ButtonActive,
                        (
                            max(0, color[0] - 30),
                            max(0, color[1] - 30),
                            max(0, color[2] - 30),
                            255,
                        ),
                        category=dpg.mvThemeCat_Core,
                    )

    def _update_appearance(self):
        """Update button appearance based on current state."""
        # Get the appropriate theme for current state
        theme_tag = f"{self.tag}_theme_{self.state.value}"

        # Apply theme to button
        dpg.bind_item_theme(self.button_tag, theme_tag)

        # Update button label
        dpg.set_item_label(self.button_tag, self.state.value)

    def _on_click(self):
        # Call external callback if set
        if self.callback:
            self.callback(self, self.state)

        self._update_appearance()

    def set_state(self, new_state):
        """
        Manually set the button state.

        Args:
            new_state: ButtonState enum value
        """
        if isinstance(new_state, ButtonState):
            self.state = new_state
            self._update_appearance()
        else:
            raise ValueError("State must be a ButtonState enum value")

    def get_state(self):
        """Get current button state."""
        return self.state

    def set_callback(self, callback_func):
        """
        Set a callback function to be called when state changes.

        Args:
            callback_func: Function that takes ButtonState as parameter
        """
        self.callback = callback_func

    def is_off(self):
        """Check if button is in OFF state."""
        return self.state == ButtonState.OFF

    def is_ignition(self):
        """Check if button is in IGNITION state."""
        return self.state == ButtonState.IGNITION

    def is_on(self):
        """Check if button is in ON state."""
        return self.state == ButtonState.ON


class DoorControlDisplay:
    def __init__(self, tag, lock_callback, unlock_callback, pos) -> None:
        self._window_tag = tag
        self._lock_callback = lock_callback
        self._unlock_callback = unlock_callback

        dpg.add_button(
            label="Doors Lock",
            callback=self._lock_callback,
            parent=self._window_tag,
            pos=pos,
        )

        dpg.add_button(
            label="Doors Unlock",
            callback=self._unlock_callback,
            parent=self._window_tag,
            pos=[pos[0], pos[1] + 30],
        )
