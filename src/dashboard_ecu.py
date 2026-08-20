#!/usr/bin/env python3
"""
Dashboard ECU
Receives CAN messages, decodes them, and displays a live dashboard.

Supports message filtering (Challenge 2):
    --filter all    -> receive Speed, RPM, Temp (default)
    --filter speed  -> receive only Speed messages
    --filter rpm    -> receive only RPM messages

Supports basic diagnostics (Challenge 7):
    If no Speed message is received for --timeout seconds,
    prints "WARNING: Vehicle ECU Offline"
"""

import can
import os
import time
import argparse

ID_SPEED = 0x100
ID_RPM = 0x101
ID_TEMP = 0x102

FILTER_SETS = {
    "all": [
        {"can_id": ID_SPEED, "can_mask": 0x7FF},
        {"can_id": ID_RPM, "can_mask": 0x7FF},
        {"can_id": ID_TEMP, "can_mask": 0x7FF},
    ],
    "speed": [{"can_id": ID_SPEED, "can_mask": 0x7FF}],
    "rpm": [{"can_id": ID_RPM, "can_mask": 0x7FF}],
}


def clear_screen():
    os.system("clear")


def main():
    parser = argparse.ArgumentParser(description="Dashboard ECU - SocketCAN receiver")
    parser.add_argument("--channel", default="vcan0", help="CAN interface (default vcan0)")
    parser.add_argument("--filter", choices=["all", "speed", "rpm"], default="all",
                         help="Which messages to receive (Challenge 2)")
    parser.add_argument("--timeout", type=float, default=5.0,
                         help="Seconds with no Speed msg before WARNING (Challenge 7)")
    parser.add_argument("--fd", action="store_true", help="Listen for CAN FD frames")
    args = parser.parse_args()

    can_filters = FILTER_SETS[args.filter]
    bus = can.interface.Bus(channel=args.channel, interface="socketcan",
                             can_filters=can_filters, fd=args.fd)

    state = {"speed": None, "rpm": None, "temp": None}
    last_speed_time = time.time()

    print(f"[Dashboard ECU] Listening on {args.channel} (filter={args.filter})")
    print("[Dashboard ECU] Press Ctrl+C to stop.\n")
    time.sleep(1)

    try:
        while True:
            msg = bus.recv(timeout=1.0)
            now = time.time()

            if msg is not None:
                if msg.arbitration_id == ID_SPEED:
                    state["speed"] = msg.data[0]
                    last_speed_time = now
                elif msg.arbitration_id == ID_RPM:
                    state["rpm"] = (msg.data[0] << 8) | msg.data[1]
                elif msg.arbitration_id == ID_TEMP:
                    state["temp"] = msg.data[0]
                else:
                    # Challenge 3: unknown message
                    print(f"[Dashboard ECU] Unknown message received: "
                          f"ID=0x{msg.arbitration_id:X} data={msg.data.hex()}")

            clear_screen()
            print("--------------------------------")
            print("Vehicle Dashboard")
            print("--------------------------------")
            print(f"Speed       : {state['speed'] if state['speed'] is not None else '--'} km/h")
            print(f"Engine RPM  : {state['rpm'] if state['rpm'] is not None else '--'} rpm")
            print(f"Temperature : {state['temp'] if state['temp'] is not None else '--'} C")
            print("--------------------------------")

            if args.filter in ("all", "speed") and (now - last_speed_time) > args.timeout:
                print("WARNING: Vehicle ECU Offline")

    except KeyboardInterrupt:
        print("\n[Dashboard ECU] Stopped.")
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
