import can

# Initialize two CAN interfaces
bus1 = can.interface.Bus(channel='vcan0', bustype='socketcan')
bus2 = can.interface.Bus(channel='vcan1', bustype='socketcan')

print("Bridging vcan0 and vcan1... Press Ctrl+C to stop.")

try:
    while True:
        # Read from vcan0 and send to vcan1
        msg = bus1.recv(timeout=0.1)
        if msg:
            bus2.send(msg)
            print(f"Forwarded from vcan0 to vcan1: {msg}")

        # Read from vcan1 and send to vcan0
        msg = bus2.recv(timeout=0.1)
        if msg:
            bus1.send(msg)
            print(f"Forwarded from vcan1 to vcan0: {msg}")

except KeyboardInterrupt:
    print("Stopped bridging.")
finally:
    bus1.shutdown()
    bus2.shutdown()
