#!/bin/bash
# Run this once per boot (or add it to a startup script) to bring up vcan0
set -e
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan 2>/dev/null || echo "vcan0 already exists"
sudo ip link set up vcan0
echo "vcan0 is up:"
ip link show vcan0
