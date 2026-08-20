#!/usr/bin/env python3
"""
Logger ECU
Records all observed CAN traffic to a CSV file.

Each log entry contains: Timestamp, Message ID, Payload Length, Payload Data
"""

import can
import csv
import time
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="Logger ECU - SocketCAN traffic logger")
    parser.add_argument("--channel", default="vcan0", help="CAN interface (default vcan0)")
    parser.add_argument("--output", default="../logs/can_log.csv", help="CSV output path")
    parser.add_argument("--fd", action="store_true", help="Listen for CAN FD frames")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    file_exists = os.path.isfile(args.output)

    bus = can.interface.Bus(channel=args.channel, interface="socketcan", fd=args.fd)

    print(f"[Logger ECU] Listening on {args.channel}, logging to {args.output}")
    print("[Logger ECU] Press Ctrl+C to stop.\n")

    with open(args.output, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "can_id_hex", "dlc", "payload_hex"])
            f.flush()

        count = 0
        try:
            while True:
                msg = bus.recv(timeout=1.0)
                if msg is None:
                    continue

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                can_id_hex = f"0x{msg.arbitration_id:X}"
                dlc = msg.dlc
                payload_hex = msg.data.hex()

                writer.writerow([timestamp, can_id_hex, dlc, payload_hex])
                f.flush()
                count += 1

                print(f"[Logger ECU] Logged #{count}: {timestamp} ID={can_id_hex} "
                      f"DLC={dlc} data={payload_hex}")

        except KeyboardInterrupt:
            print(f"\n[Logger ECU] Stopped. {count} messages logged to {args.output}")
        finally:
            bus.shutdown()


if __name__ == "__main__":
    main()
