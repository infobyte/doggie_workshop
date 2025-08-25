from doggie_lab.car import Car, CarBuilder
from doggie_lab.gui.window import Window
import argparse
import sys
import signal


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Car CAN bus interface controller")

    # Create mutually exclusive group for CAN interface types
    group = parser.add_mutually_exclusive_group(required=True)

    # Serial interface options
    group.add_argument(
        '--serial',
        nargs=2,
        metavar=('TX_PORT', 'RX_PORT'),
        help='Use serial interfaces with ports and baudrates (e.g., /dev/ttyUSB0@115200 /dev/ttyUSB1@8600)'
    )

    # SocketCAN interface options
    group.add_argument(
        '--socketcan',
        nargs=2,
        metavar=('TX_CAN', 'RX_CAN'),
        help='Use socketCAN interfaces (e.g., can0 can1)'
    )

    # CAN bus speed argument
    parser.add_argument(
        '--speed',
        type=int,
        default=500000,
        help='CAN bus speed in bits per second (default: 500000)'
    )

    return parser.parse_args()


def signal_handler(sig, frame, car: Car, window: Window):
    """Handle Ctrl+C signal."""
    print("\nCtrl+C pressed. Stopping car...")
    car.stop()
    window.clean()
    sys.exit(0)


def main():
    # Parse arguments
    args = parse_arguments()

    window = Window()

    # Create car instance with instrument cluster and CAN bus
    car: Car
    if args.serial is not None:
        car = CarBuilder.from_serial(*args.serial, speed=args.speed)

    else:
        car = CarBuilder.from_socketcan(*args.socketcan, speed=args.speed)

    car.start()
    print("Car running")

    # Setup signal handler for Ctrl+C
    signal.signal(
        signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, car, window)
    )

    # Keep main thread running
    try:
        window.run()
        window.clean()
        car.stop()

    except KeyboardInterrupt:
        # This should be handled by signal handler
        pass


if __name__ == "__main__":
    main()
