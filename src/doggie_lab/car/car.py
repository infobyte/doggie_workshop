import can
from doggie_lab.ecus.ecu import Ecu
from doggie_lab.ecus.ecu_ui import UiEcu
import glob
import importlib.util
import inspect
import os
from pathlib import Path


class Car:
    """
    Acts as the central controller for all car systems and ECUs.
    """

    def __init__(self, bus: can.BusABC, notifier: can.Notifier):
        self._bus = bus
        self._notifier = notifier

        ecus_clss = Car._get_ecu_classes()
        self._ecus = [Ecu(self._bus, self._notifier) for Ecu in ecus_clss]

    @staticmethod
    def _get_ecu_classes():
        """
        Dynamically imports classes that inherit from ecu_base_class from *.py files
        in the specified directory and returns them in a list.

        Args:
            ecu_base_class: The base class (Ecu) to check inheritance against
            ecus_dir: Directory containing the *.py files (default: /ecus)

        Returns:
            List of classes that inherit from ecu_base_class
        """
        ecu_classes = []

        # Get the project root directory (assuming this script is in the project)
        project_root = Path(__file__).resolve().parent.parent

        # Construct path to ecus directory
        ecus_path = project_root / "ecus"

        # Find all *_ecu.py files
        ecu_files = glob.glob(os.path.join(ecus_path, "*_ecu.py"))

        for file_path in ecu_files:
            try:
                # Get module name from file
                module_name = Path(file_path).stem

                # Create module spec
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None:
                    continue

                # Create module
                module = importlib.util.module_from_spec(spec)

                # Execute module
                spec.loader.exec_module(module)

                # Get all classes from module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if class inherits from ecu_base_class and is not the base class itself
                    if issubclass(obj, Ecu) and obj not in [Ecu, UiEcu]:
                        ecu_classes.append(obj)

            except Exception as e:
                print(f"Error importing {file_path}: {str(e)}")
                continue

        return ecu_classes

    def start(self):
        # Start all the ECUs
        for ecu in self._ecus:
            ecu.start()

    def stop(self):
        # Stop all the ECUs
        for ecu in self._ecus:
            ecu.stop()
