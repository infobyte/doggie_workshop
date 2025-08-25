from doggie_lab.ecus.ecu_ui import UiEcu
from doggie_lab.messages.immo_message import KeyMessage
import dearpygui.dearpygui as dpg
import can
import time


class ImmoEcu(UiEcu):
    KEY_INSERTED = 0x1
    KEY_NOT_INSERTED = 0x0

    def __init__(self, bus: can.BusABC, notifier: can.Notifier):
        super().__init__(bus, notifier, "Immo ECU")
        self.key_inserted = True
        self._init_ui()

    def _init_ui(self):
        dpg.add_checkbox(
            label="Key inserted",
            default_value=True,
            callback=self._insert_key,
            parent=self._window_tag,
        )

    def _insert_key(self, sender, app_data, user_data):
        self.key_inserted = app_data

    def loop(self):
        while True:
            time.sleep(.001)
            self.send_msg(KeyMessage(self.key_inserted).to_can_msg())
