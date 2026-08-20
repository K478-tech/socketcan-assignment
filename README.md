# SocketCAN Assignment

Software-only CAN network demo using Linux SocketCAN (vcan0). Three nodes:
Vehicle ECU (sender), Dashboard ECU (receiver/display), Logger ECU (CSV logger).

## Setup

```bash
sudo apt update
sudo apt install -y can-utils python3-pip
pip3 install python-can --break-system-packages

# Bring up the virtual CAN interface (repeat after every reboot)
./setup_vcan.sh
```

## Running

Open three terminals, all inside `src/`:

```bash
# Terminal 1
python3 vehicle_ecu.py

# Terminal 2
python3 dashboard_ecu.py

# Terminal 3
python3 logger_ecu.py
```

## Challenge commands

```bash
# Challenge 2: filtering
python3 dashboard_ecu.py --filter speed
python3 dashboard_ecu.py --filter rpm

# Challenge 3: inject unknown message
cansend vcan0 200#AABBCCDD

# Challenge 4: transmission rate
python3 vehicle_ecu.py --interval 0.1
python3 vehicle_ecu.py --interval 2.0

# Challenge 6: CAN FD
sudo ip link set vcan0 mtu 72          # enable FD-size MTU on vcan0
python3 vehicle_ecu.py --fd
python3 dashboard_ecu.py --fd
python3 logger_ecu.py --fd

# Challenge 7: diagnostics — start Dashboard, then kill Vehicle ECU and watch
# for "WARNING: Vehicle ECU Offline" after the timeout (default 5s)
```

## Project structure

```
socketcan-assignment/
├── README.md
├── setup_vcan.sh
├── src/
│   ├── vehicle_ecu.py
│   ├── dashboard_ecu.py
│   └── logger_ecu.py
├── logs/
│   └── can_log.csv        (generated at runtime)
└── docs/
    └── REPORT_TEMPLATE.md
```
