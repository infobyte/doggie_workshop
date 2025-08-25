from can import BusABC, Message, Notifier
import queue
from abc import ABC, abstractmethod
import threading
import time


class Ecu(ABC):
    """Base class for CAN ECUs that listen for messages and queue responses."""

    def __init__(
         self, bus: BusABC, notifier: Notifier, ecu_name: str = "BaseEcu"
    ):
        ABC.__init__(self)
        self.ecu_name = ecu_name
        self.bus = bus
        self.msg_queue = queue.Queue()
        self.notifier = notifier
        self.running = False
        self.thread = None

    def start(self):
        """Start the ECU thread."""
        print(f"Starting {self.ecu_name}...")
        if self.thread is not None and self.thread.is_alive():
            return

        self.running = True
        self.notifier.add_listener(self.on_message_received)
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the ECU thread."""
        print(f"Stopping {self.ecu_name}...")
        self.running = False
        self.notifier.remove_listener(self.on_message_received)
        if self.thread is not None:
            self.thread.join(timeout=1.0)

    def get_msg(self) -> Message:
        msg = self.msg_queue.get()
        self.msg_queue.task_done()
        # print(f"{self.ecu_name} received message: {msg}")
        return msg

    def send_msg(self, msg: Message):
        msg.is_extended_id = False
        self.bus.send(msg)
        # print(f"{self.ecu_name} sent message: {msg}")

    def on_message_received(self, msg: Message):
        """Handle incoming CAN messages."""
        # print(f"{self.ecu_name} on_message_received received message: {msg}")
        try:
            self.msg_queue.put(msg)
        except Exception as e:
            print(f"Error passing message to {self.ecu_name}: {e}")

    def _run(self):
        """Main loop for the response sender thread."""
        while self.running:
            self.loop()

            time.sleep(1)

    @abstractmethod
    def loop(self):
        pass
