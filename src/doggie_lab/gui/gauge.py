import math
import dearpygui.dearpygui as dpg

class Gauge:
    def __init__(self, parent_tag, center_x, center_y, radius, min_angle=-135, max_angle=135,
                 min_value=0, max_value=240, units="", label="", tick_interval=None,
                 needle_color=(255, 0, 0, 255), background_color=(150, 150, 150, 255),
                 text_color=(255, 255, 255, 255), tick_color=(200, 200, 200, 255),
                 needle_thickness=3, background_thickness=2, needle_length_ratio=0.9,
                 decimal_places=0):
        """
        Generic gauge class for instrument cluster

        Args:
            parent_tag: Dear PyGui parent tag for drawing
            center_x, center_y: Center position of the gauge
            radius: Radius of the gauge arc
            min_angle, max_angle: Angle range in degrees (-135 to 135 for semicircle)
            min_value, max_value: Value range for the gauge
            units: Unit string to display (e.g., "km/h", "RPM", "°C")
            label: Label text to display below the gauge value
            tick_interval: Interval for tick marks (auto-calculated if None)
            needle_color: Color of the needle (R, G, B, A)
            background_color: Color of the background arc
            text_color: Color of the value text
            tick_color: Color of the tick labels
            needle_thickness: Thickness of the needle line
            background_thickness: Thickness of the background arc
            needle_length_ratio: Length of needle as ratio of radius (0.0 to 1.0)
        """
        self.parent_tag = parent_tag
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_value = min_value
        self.max_value = max_value
        self.units = units
        self.label = label
        self.needle_color = needle_color
        self.background_color = background_color
        self.text_color = text_color
        self.tick_color = tick_color
        self.needle_thickness = needle_thickness
        self.background_thickness = background_thickness
        self.needle_length_ratio = needle_length_ratio
        self.decimal_places = decimal_places

        # Track dynamic elements for efficient updates
        self.gauge_id = f"gauge_{center_x}_{center_y}"
        self.needle_tag = f"{self.gauge_id}_needle"
        self.center_dot_tag = f"{self.gauge_id}_center"
        self.value_text_tag = f"{self.gauge_id}_value"
        self.label_text_tag = f"{self.gauge_id}_label"
        self.static_drawn = False

        # Auto-calculate tick interval if not provided
        if tick_interval is None:
            value_range = max_value - min_value
            if value_range <= 10:
                self.tick_interval = 1
            elif value_range <= 50:
                self.tick_interval = 5
            elif value_range <= 100:
                self.tick_interval = 10
            elif value_range <= 500:
                self.tick_interval = 50
            else:
                self.tick_interval = 100
        else:
            self.tick_interval = tick_interval

    def value_to_angle(self, value):
        """Convert a value to its corresponding angle in degrees"""
        # Clamp value to valid range
        value = max(self.min_value, min(self.max_value, value))

        # Convert to angle
        value_ratio = (value - self.min_value) / (self.max_value - self.min_value)
        return self.min_angle + (self.max_angle - self.min_angle) * value_ratio

    def draw_static_elements(self):
        """Draw the static elements of the gauge (background arc and tick labels)"""
        if self.static_drawn:
            return  # Static elements already drawn

        # Draw background arc (using segments to simulate an arc)
        num_segments = 60
        for i in range(num_segments + 1):
            t = i / num_segments
            segment_angle = math.radians(self.min_angle + t * (self.max_angle - self.min_angle))
            x1 = self.center_x + self.radius * math.cos(segment_angle)
            y1 = self.center_y + self.radius * math.sin(segment_angle)
            x2 = self.center_x + (self.radius + 4) * math.cos(segment_angle)
            y2 = self.center_y + (self.radius + 4) * math.sin(segment_angle)
            dpg.draw_line((x1, y1), (x2, y2), color=self.background_color,
                         thickness=self.background_thickness, parent=self.parent_tag)

        # Draw tick labels
        tick_value = self.min_value
        while tick_value <= self.max_value:
            tick_angle_deg = self.value_to_angle(tick_value)
            tick_angle_rad = math.radians(tick_angle_deg)

            # Position tick label
            label_radius = self.radius + 15
            tick_x = self.center_x + label_radius * math.cos(tick_angle_rad)
            tick_y = self.center_y + label_radius * math.sin(tick_angle_rad)

            # Adjust text position for better centering
            tick_text = f"{int(tick_value)}"
            text_offset_x = len(tick_text) * 3
            text_offset_y = 6

            dpg.draw_text((tick_x - text_offset_x, tick_y - text_offset_y),
                         tick_text, size=12, color=self.tick_color, parent=self.parent_tag)

            tick_value += self.tick_interval

        self.static_drawn = True

    def update_dynamic_elements(self, value):
        """Update only the dynamic elements (needle and value text)"""
        # Delete existing dynamic elements
        if dpg.does_item_exist(self.needle_tag):
            dpg.delete_item(self.needle_tag)
        if dpg.does_item_exist(self.center_dot_tag):
            dpg.delete_item(self.center_dot_tag)
        if dpg.does_item_exist(self.value_text_tag):
            dpg.delete_item(self.value_text_tag)
        if dpg.does_item_exist(self.label_text_tag):
            dpg.delete_item(self.label_text_tag)

        # Calculate needle angle
        angle_deg = self.value_to_angle(value)
        angle_rad = math.radians(angle_deg)

        # Draw needle
        needle_length = self.radius * self.needle_length_ratio
        needle_x = self.center_x + needle_length * math.cos(angle_rad)
        needle_y = self.center_y + needle_length * math.sin(angle_rad)
        dpg.draw_line((self.center_x, self.center_y), (needle_x, needle_y),
                     color=self.needle_color, thickness=self.needle_thickness,
                     parent=self.parent_tag, tag=self.needle_tag)

        # Draw center dot
        dpg.draw_circle((self.center_x, self.center_y), 5, color=self.needle_color,
                       fill=self.needle_color, parent=self.parent_tag, tag=self.center_dot_tag)

        # Draw value text
        value_text = f"{value:.{self.decimal_places}f}"
        if self.units:
            value_text += f" {self.units}"

        text_x = self.center_x - len(value_text) * 6  # Rough centering
        text_y = self.center_y + self.radius + 25
        dpg.draw_text((text_x, text_y), value_text, size=20, color=self.text_color,
                     parent=self.parent_tag, tag=self.value_text_tag)

        # Draw label if provided
        if self.label:
            label_x = self.center_x - len(self.label) * 4  # Rough centering
            label_y = self.center_y + self.radius + 50
            dpg.draw_text((label_x, label_y), self.label, size=14, color=self.text_color,
                         parent=self.parent_tag, tag=self.label_text_tag)

    def draw(self, value):
        """
        Draw the complete gauge (static elements once, then dynamic elements)

        Args:
            value: Current value to display
        """
        # Draw static elements if not already drawn
        self.draw_static_elements()

        # Update dynamic elements
        self.update_dynamic_elements(value)

    def update_value(self, value):
        """Update the gauge with a new value (only redraws needle and text)"""
        # Ensure static elements are drawn
        self.draw_static_elements()

        # Update only the dynamic parts
        self.update_dynamic_elements(value)


class SpeedometerGauge(Gauge):
    """Preconfigured speedometer gauge"""
    def __init__(self, parent_tag, center_x, center_y, radius=100):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            min_angle=-135,
            max_angle=135,
            min_value=0,
            max_value=240,
            units="km/h",
            label="SPEED",
            tick_interval=40,
            needle_color=(255, 0, 0, 255),
            decimal_places=1
        )


class TachometerGauge(Gauge):
    """Preconfigured tachometer gauge"""
    def __init__(self, parent_tag, center_x, center_y, radius=100):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            min_angle=-135,
            max_angle=135,
            min_value=0,
            max_value=8000,
            units="RPM",
            label="ENGINE",
            tick_interval=1000,
            needle_color=(0, 255, 0, 255)
        )


class FuelGauge(Gauge):
    """Preconfigured fuel gauge"""
    def __init__(self, parent_tag, center_x, center_y, radius=80):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            min_angle=-45,
            max_angle=45,
            min_value=0,
            max_value=100,
            units="%",
            label="FUEL",
            tick_interval=25,
            needle_color=(255, 165, 0, 255)  # Orange
        )


class TemperatureGauge(Gauge):
    """Preconfigured temperature gauge"""
    def __init__(self, parent_tag, center_x, center_y, radius=80):
        super().__init__(
            parent_tag=parent_tag,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            min_angle=-45,
            max_angle=45,
            min_value=60,
            max_value=120,
            units="°C",
            label="TEMP",
            tick_interval=20,
            needle_color=(0, 0, 255, 255)  # Blue
        )
