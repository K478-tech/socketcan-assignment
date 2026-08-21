# SocketCAN Automotive Communication Network

A software-only automotive communication network developed using **Linux SocketCAN** and **Virtual CAN (`vcan0`)**.

This project simulates communication between multiple Electronic Control Units (ECUs) without requiring physical CAN hardware.

The system consists of:

- Vehicle ECU
- Dashboard ECU
- Logger ECU

The project demonstrates CAN communication, message filtering, logging, unknown message handling, transmission-rate experiments, node-failure detection, diagnostics, and CAN FD communication.

---

## 1. Project Overview

Modern vehicles use Controller Area Network (CAN) to allow different Electronic Control Units (ECUs) to communicate reliably.

This project recreates a small automotive CAN network using Linux SocketCAN and a virtual CAN interface.

The following ECUs are simulated:

### Vehicle ECU

Generates and transmits vehicle information such as:

- Vehicle Speed
- Engine RPM
- Coolant Temperature

### Dashboard ECU

Receives CAN messages and displays vehicle information.

It also supports:

- Receiving all CAN messages
- Speed-only filtering
- RPM-only filtering
- Unknown CAN message detection
- Vehicle ECU failure detection

### Logger ECU

Continuously monitors the CAN network and records received messages into a CSV file containing:

- Timestamp
- CAN ID
- DLC
- Payload data

---

## 2. Technologies Used

- Linux
- Python 3
- SocketCAN
- Virtual CAN (`vcan0`)
- `python-can`
- CAN Bus
- CAN FD
- CSV logging
- Git and GitHub

---

## 3. System Architecture

```text
                         Linux System
                 ┌─────────────────────────┐
                 │       SocketCAN         │
                 │       vcan0 interface   │
                 └────────────┬────────────┘
                              │
                    CAN frames / broadcast
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │ Vehicle ECU │ │ Dashboard   │ │  Logger ECU │
       │  (Sender)   │ │    ECU      │ │  (Receiver) │
       └─────────────┘ └─────────────┘ └─────────────┘
              │               │                │
              │               ▼                ▼
              │        Live vehicle data    can_log.csv
              │        Speed/RPM/Temp       (CSV log)
              │
              └────────── CAN messages ──────────────►
```


All ECUs communicate through the same Linux virtual CAN interface.

---

## 4. CAN Message Definitions

The project uses standard 11-bit CAN identifiers.

| CAN ID | Signal | DLC | Description |
|--------|--------|-----|-------------|
| `0x100` | Vehicle Speed | 1 byte | Vehicle speed in km/h |
| `0x101` | Engine RPM | 2 bytes | Engine speed in RPM |
| `0x102` | Coolant Temperature | 1 byte | Engine coolant temperature |
| `0x200` | Unknown/Test Message | Variable | Used for unknown-message testing |

### Message Ranges

| Signal | Range |
|--------|-------|
| Vehicle Speed | 0–120 km/h |
| Engine RPM | 800–5000 RPM |
| Coolant Temperature | 20–120 °C |

---

## 5. Project Structure

```text
socketcan-assignment/
│
├── README.md
├── setup_vcan.sh
│
├── src/
│   ├── vehicle_ecu.py
│   ├── dashboard_ecu.py
│   └── logger_ecu.py
│
├── docs/
│   └── REPORT.md
│
└── logs/
    └── can_log.csv
```

### File Description

| File | Purpose |
|------|---------|
| `setup_vcan.sh` | Creates and configures the virtual CAN interface |
| `vehicle_ecu.py` | Generates and transmits vehicle CAN messages |
| `dashboard_ecu.py` | Receives, filters and displays CAN messages |
| `logger_ecu.py` | Logs CAN traffic to CSV |
| `REPORT.md` | Complete technical report |
| `can_log.csv` | CAN message log |

---

## 6. Installation

### Requirements

Use a Linux system with:

- Python 3
- Linux SocketCAN
- `can-utils`
- `python-can`

Install the required packages:

```bash
sudo apt update
sudo apt install can-utils python3 python3-pip
```

Install the Python CAN library:

```bash
pip3 install python-can
```

---

## 7. Setup Virtual CAN

Navigate to the project:

```bash
cd ~/socketcan-assignment
```

Run:

```bash
./setup_vcan.sh
```

The script creates the virtual CAN interface:

```text
vcan0
```

Verify the interface:

```bash
ip link show vcan0
```

You can also monitor CAN traffic using:

```bash
candump vcan0
```

---

## 8. Running the ECUs

The three ECUs should normally be run in separate terminal windows.

### Terminal 1 – Vehicle ECU

```bash
cd ~/socketcan-assignment
python3 src/vehicle_ecu.py
```

The Vehicle ECU continuously generates and transmits:

- Speed
- RPM
- Temperature

### Terminal 2 – Dashboard ECU

```bash
cd ~/socketcan-assignment
python3 src/dashboard_ecu.py --filter all
```

The Dashboard ECU displays received CAN messages.

### Terminal 3 – Logger ECU

```bash
cd ~/socketcan-assignment
python3 src/logger_ecu.py
```

The Logger ECU records received CAN traffic.

The log is stored in:

```text
logs/can_log.csv
```

---

## 9. Monitoring CAN Traffic

Linux provides the `candump` utility for observing CAN frames.

Run:

```bash
candump vcan0
```

Example:

```text
vcan0  100   [1]  3A
vcan0  101   [2]  0C 80
vcan0  102   [1]  50
```

This allows the complete CAN traffic on the virtual bus to be observed.

---

## 10. Assignment Challenges

### Challenge 1 – CAN Traffic Observation

The virtual CAN interface is monitored using:

```bash
candump vcan0
```

This demonstrates that multiple ECUs can communicate through the same CAN interface.

The Vehicle ECU generates messages while the Dashboard ECU and Logger ECU receive them independently.

### Challenge 2 – CAN Message Filtering

The Dashboard ECU supports selective reception of CAN messages.

#### Receive all CAN messages

```bash
python3 src/dashboard_ecu.py --filter all
```

#### Receive only Speed messages

```bash
python3 src/dashboard_ecu.py --filter speed
```

#### Receive only RPM messages

```bash
python3 src/dashboard_ecu.py --filter rpm
```

SocketCAN filtering is used so that the application can selectively receive required CAN identifiers.

### Challenge 3 – Unknown CAN Message

An unknown CAN message can be injected using:

```bash
cansend vcan0 200#AABBCCDD
```

The message uses CAN ID:

```text
0x200
```

which is not one of the normal vehicle messages.

The Dashboard ECU can identify the message as unknown, while the Logger ECU records it as part of the CAN traffic.

This demonstrates how applications can handle unexpected CAN messages.

### Challenge 4 – Transmission Rate

The Vehicle ECU supports configurable transmission intervals.

For example:

```bash
python3 src/vehicle_ecu.py --interval 0.1
```

The `--interval` option controls the delay between transmitted messages.

This allows the effect of different CAN traffic rates to be studied.

A smaller interval produces higher CAN traffic, while a larger interval produces lower traffic.

### Challenge 5 – Node Failure

The Vehicle ECU can be stopped while the Dashboard ECU continues running.

The Dashboard ECU monitors the time since the last Vehicle ECU message.

If no message is received for the configured timeout period, the Dashboard reports:

```text
WARNING: Vehicle ECU Offline
```

This demonstrates a basic ECU node-failure detection mechanism.

### Challenge 6 – CAN FD

The project also supports CAN FD mode.

Run the Vehicle ECU using:

```bash
python3 src/vehicle_ecu.py --fd
```

Run the Dashboard ECU using:

```bash
python3 src/dashboard_ecu.py --filter all --fd
```

Run the Logger ECU using:

```bash
python3 src/logger_ecu.py --fd
```

CAN FD extends the capabilities of Classical CAN by supporting larger payloads and higher data-phase bit rates.

### Challenge 7 – ECU Diagnostics

The Dashboard ECU includes a timeout-based diagnostic mechanism.

Example:

```bash
python3 src/dashboard_ecu.py --filter all --timeout 2
```

If the Vehicle ECU stops transmitting for longer than the configured timeout, the Dashboard ECU reports that the Vehicle ECU is offline.

This demonstrates a simple automotive diagnostic concept based on message timeout monitoring.

---

## 11. CAN vs CAN FD

| Feature | Classical CAN | CAN FD |
|---------|---------------|--------|
| Maximum payload | 8 bytes | Up to 64 bytes |
| Data rate | Lower | Higher data-phase rate |
| Frame format | CAN | CAN FD |
| Larger payloads | No | Yes |
| Compatibility | Traditional CAN nodes | Requires CAN FD capable nodes |

CAN FD is useful for modern automotive systems because it allows more information to be transmitted in a single frame and can provide higher data throughput.

---

## 12. Logging

The Logger ECU records CAN traffic in:

```text
logs/can_log.csv
```

The log contains information such as:

```text
Timestamp
CAN ID
DLC
Payload
```

Example:

```text
2026-08-20 21:30:12,100,1,3A
2026-08-20 21:30:12,101,2,0C80
2026-08-20 21:30:12,102,1,50
```

This provides a simple record of the communication taking place on the CAN network.

---

## 13. Useful Commands

### Check CAN interface

```bash
ip link show vcan0
```

### Monitor CAN traffic

```bash
candump vcan0
```

### Send a test CAN frame

```bash
cansend vcan0 200#AABBCCDD
```

### Check CAN interface statistics

```bash
ip -details -statistics link show vcan0
```

---

## 14. Command Summary

### Start virtual CAN

```bash
./setup_vcan.sh
```

### Vehicle ECU

```bash
python3 src/vehicle_ecu.py
```

### Vehicle ECU with custom transmission interval

```bash
python3 src/vehicle_ecu.py --interval 0.1
```

### Vehicle ECU in CAN FD mode

```bash
python3 src/vehicle_ecu.py --fd
```

### Dashboard – all messages

```bash
python3 src/dashboard_ecu.py --filter all
```

### Dashboard – Speed only

```bash
python3 src/dashboard_ecu.py --filter speed
```

### Dashboard – RPM only

```bash
python3 src/dashboard_ecu.py --filter rpm
```

### Dashboard – CAN FD

```bash
python3 src/dashboard_ecu.py --filter all --fd
```

### Logger

```bash
python3 src/logger_ecu.py
```

### Logger – CAN FD

```bash
python3 src/logger_ecu.py --fd
```

### Monitor traffic

```bash
candump vcan0
```

---

## 15. Key Learnings

Through this assignment, the following concepts were demonstrated:

- Linux SocketCAN architecture
- CAN as a Linux network interface
- Virtual CAN using `vcan0`
- CAN frame transmission and reception
- CAN identifiers and payloads
- SocketCAN hardware-independent communication
- CAN message filtering
- Multi-ECU communication
- CAN traffic monitoring
- CAN message logging
- Unknown message handling
- Transmission-rate experiments
- ECU node-failure detection
- Basic automotive diagnostics
- CAN FD communication

---

## 16. Technical Report

The complete technical report for this assignment is available in:

```text
docs/REPORT.md
```

The report contains the investigation, architecture, CAN message definitions, implementation details, challenge results, CAN FD discussion, observations, key learnings and conclusion.

---

## 17. Assignment Completion Status

| Assignment Component | Status |
|-----------------------|--------|
| SocketCAN Investigation | Completed |
| CAN Network Discovery | Completed |
| CAN Message and Signal Mapping | Completed |
| Vehicle ECU | Completed |
| Dashboard ECU | Completed |
| Logger ECU | Completed |
| CAN Traffic Observation | Completed |
| CAN Filtering | Completed |
| Unknown Message Handling | Completed |
| Transmission Rate Experiment | Completed |
| Node Failure Detection | Completed |
| CAN FD Support | Completed |
| ECU Diagnostics | Completed |
| Technical Report | Completed |

---

## 18. Conclusion

This project demonstrates how a small automotive communication network can be implemented entirely in software using Linux SocketCAN and Virtual CAN.

The three simulated ECUs communicate through the `vcan0` interface without requiring physical CAN hardware.

The implementation demonstrates important automotive networking concepts including CAN message transmission, reception, filtering, logging, fault detection, diagnostics and CAN FD communication.

The project provides a practical understanding of how Linux can be used as a platform for developing and testing automotive communication systems before deployment on physical CAN hardware.
