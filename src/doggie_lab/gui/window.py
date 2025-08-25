import dearpygui.dearpygui as dpg
from importlib.resources import files


class Window:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Dear PyGui setup
        dpg.create_context()
        dpg.configure_app(docking=True, docking_space=True)
        dpg.create_viewport(title="Doggie Lab", width=800, height=600)

        file_path = files("doggie_lab.data") / "custom_layout.ini"
        dpg.set_init_file(file=file_path)

    def run(self):
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()

    def clean(self):
        dpg.destroy_context()
