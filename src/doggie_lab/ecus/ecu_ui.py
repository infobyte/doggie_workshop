from doggie_lab.ecus.ecu import Ecu
from can import BusABC, Notifier
import dearpygui.dearpygui as dpg

class UiEcu(Ecu):
    def __init__(
                 self,
                 bus: BusABC,
                 notifier: Notifier,
                 ecu_name: str = "BaseEcu",
        ):
        super().__init__(bus, notifier, ecu_name)

        self._window_tag = dpg.generate_uuid()

        dpg.add_window(label=self.ecu_name, tag=self._window_tag)
