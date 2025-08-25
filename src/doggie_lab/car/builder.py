import can
from doggie_lab.car.car import Car
from doggie_lab.car.proxy_bus import ProxyBus


class CarBuilder:
    @staticmethod
    def from_serial(tx_port: str, rx_port: str, speed: int) -> Car:
        tx_bus = can.ThreadSafeBus(bustype="slcan", channel=tx_port, bitrate=speed)
        rx_bus = can.ThreadSafeBus(bustype="slcan", channel=rx_port, bitrate=speed)

        return CarBuilder._build(tx_bus, rx_bus)

    @staticmethod
    def from_socketcan(tx_if: str, rx_if: str, speed: int) -> Car:
        tx_bus = can.ThreadSafeBus(bustype="socketcan", channel=tx_if)
        rx_bus = can.ThreadSafeBus(bustype="socketcan", channel=rx_if)

        return CarBuilder._build(tx_bus, rx_bus)

    def _build(tx_bus: can.BusABC, rx_bus: can.BusABC) -> Car:
        proxy_bus = ProxyBus(tx_bus, rx_bus)
        notifier = can.Notifier(proxy_bus, [])

        return Car(proxy_bus, notifier)
