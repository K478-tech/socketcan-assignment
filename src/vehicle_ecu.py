#!/usr/bin/env python3
"""
Vehicle ECU
Transmits Vehicle Speed, Engine RPM, and Coolant Temperature over SocketCAN.

CAN Message Definitions:
    0x100  Vehicle Speed        (1 byte, 0-120 km/h)
    0x101  Engine RPM           (2 bytes, 800-5000 rpm, big-endian)
    0x102  Coolant Temperature  (1 byte, 20-120 C)
"""

import can
import time
import random
import argparse

ID_SPEED = 0x100
ID_RPM = 0x101
ID_TEMP = 0x102


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def main():
    parser = argparse.ArgumentParser(description="Vehicle ECU - SocketCAN sender")
    parser.add_argument("--channel", default="vcan0", help="CAN interface (default vcan0)")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between transmissions")
    parser.add_argument("--fd", action="store_true", help="Send as CAN FD frames")
    args = parser.parse_args()

    bus = can.interface.Bus(channel=args.channel, interface="socketcan", fd=args.fd)

    speed = 40.0
    rpm = 1500.0
    temp = 60.0

    print(f"[Vehicle ECU] Starting on {args.channel} (interval={args.interval}s, fd={args.fd})")
    print("[Vehicle ECU] Press Ctrl+C to stop.\n")

    try:
        while True:
            speed = clamp(speed + random.uniform(-5, 5), 0, 120)
            rpm = clamp(rpm + random.uniform(-150, 150), 800, 5000)
            temp = clamp(temp + random.uniform(-1, 1), 20, 120)

            speed_i = int(speed)
            rpm_i = int(rpm)
            temp_i = int(temp)

            msg_speed = can.Message(
                arbitration_id=ID_SPEED,
                data=[speed_i],
                is_extended_id=False,
                is_fd=args.fd,
            )
            msg_rpm = can.Message(
                arbitration_id=ID_RPM,
                data=[(rpm_i >> 8) & 0xFF, rpm_i & 0xFF],
                is_extended_id=False,
                is_fd=args.fd,
            )
            msg_temp = can.Message(
                arbitration_id=ID_TEMP,
                data=[temp_i],
                is_extended_id=False,
                is_fd=args.fd,
            )

            bus.send(msg_speed)
            bus.send(msg_rpm)
            bus.send(msg_temp)

            print(f"[Vehicle ECU] Speed={speed_i:3d} km/h  RPM={rpm_i:4d}  Temp={temp_i:3d} C")

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[Vehicle ECU] Stopped.")
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
