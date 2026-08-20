# SocketCAN Assignment — Technical Report

---

## 1. SocketCAN Overview (Task 1)

### What is SocketCAN?

SocketCAN is the Linux implementation of the Controller Area Network (CAN) communication stack. Instead of treating CAN as a device that needs a separate vendor-specific software library, Linux provides CAN as a network protocol family. Applications can therefore communicate with CAN using the normal socket-based communication approach used for other Linux networking applications.

In this assignment, SocketCAN was used with a virtual CAN interface called `vcan0`. This allowed the complete CAN communication system to be tested without any physical CAN controller, CAN transceiver, or vehicle hardware. The provided setup script loads the `vcan` module, creates `vcan0`, and brings the interface up.

The assignment uses three software nodes:

- **Vehicle ECU:** generates and transmits vehicle data.
- **Dashboard ECU:** receives the CAN messages and displays Speed, RPM and Temperature.
- **Logger ECU:** receives the CAN traffic and stores it in a CSV file.

The Vehicle ECU sends three types of messages. Vehicle Speed uses CAN ID `0x100`, Engine RPM uses `0x101`, and Coolant Temperature uses `0x102`. The Vehicle ECU code sends these messages through the SocketCAN interface using the `python-can` library.

### Why is CAN treated as a network interface in Linux?

Linux represents CAN as a network interface because CAN is a communication network between multiple nodes. This approach makes CAN communication fit naturally into the Linux networking architecture. Applications can use standard socket operations to communicate with the CAN interface rather than depending on a special character-device interface or a vendor-specific API.

The main advantage can be seen during this assignment: multiple applications were able to listen to the same `vcan0` interface at the same time. The Dashboard and Logger both received the same vehicle messages while the Vehicle ECU was transmitting. This made it possible to display the data and log it simultaneously without requiring separate communication channels.

SocketCAN also allows common Linux networking tools and commands to be used with CAN. The CAN interface can be inspected and configured using commands such as `ip link`, while CAN utilities such as `candump` and `cansend` can be used to observe and generate traffic.

### SocketCAN compared with vendor-specific CAN APIs

Vendor-specific CAN APIs are normally designed around a particular manufacturer's hardware and software environment. Examples include Vector XL Driver, PEAK PCAN-Basic and Kvaser CANlib. Applications written directly for such APIs may need changes when the CAN hardware or vendor changes.

SocketCAN provides a more hardware-independent approach. An application communicates with a SocketCAN interface instead of directly depending on a particular CAN hardware vendor. In this assignment, the same application communicates with `vcan0`, which is a virtual interface. The same SocketCAN-based application architecture can also be used with a real CAN interface when an appropriate Linux SocketCAN driver is available.

### Advantages of the SocketCAN architecture

The main advantages observed from this assignment are:

1. **No physical CAN hardware is required for basic testing.** The `vcan0` interface provides a software-only CAN network.
2. **Multiple applications can listen simultaneously.** Dashboard and Logger were able to receive the same traffic.
3. **Standard Linux socket architecture is used.** Applications can use the CAN interface in a familiar networking model.
4. **Message filtering is supported.** The Dashboard can select only Speed or only RPM messages.
5. **Linux CAN tools can be used for testing.** For example, `cansend` was used to inject an unknown CAN message.
6. **The system is suitable for software-first development.** Communication logic can be developed and tested before physical automotive hardware is available.

Overall, SocketCAN provides a clean way to integrate CAN communication into Linux applications. This assignment showed that a complete small automotive communication system can be created and tested using only software, while still demonstrating important CAN concepts such as message IDs, filtering, broadcast communication, logging and diagnostics.

---

## 2. Architecture (Task 2)

The architecture used in this assignment is based on a virtual CAN network. The three ECU applications communicate through the same `vcan0` interface.

### Architecture Diagram

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

### CAN interface types

Three important CAN interface types relevant to this assignment are:

- **vcan:** A virtual CAN interface. It is useful for software testing because it does not require physical CAN hardware. This assignment uses `vcan0`.
- **can:** Represents a real CAN network interface provided through an appropriate CAN hardware driver.
- **slcan:** Serial Line CAN, where CAN communication is accessed through a serial connection to a CAN adapter.

For this project, `vcan0` was selected because the assignment is designed as a software-only CAN network.

### How applications connect to CAN

At the Linux level, CAN is provided through the CAN protocol family. Applications can use CAN raw sockets (`AF_CAN` with `SOCK_RAW`) to communicate with the CAN interface.

In this project, the Python applications use the `python-can` library with the SocketCAN interface. The Vehicle ECU creates a CAN bus connection on `vcan0`, and the Dashboard and Logger create their own connections to the same interface.

The important point is that the applications do not communicate directly with one another. They communicate through the SocketCAN CAN interface.

### How multiple applications communicate simultaneously

CAN communication follows a broadcast-style bus model. A transmitted frame is available to the applications that have sockets bound to the interface, subject to their configured filters.

This was directly observed during the experiment. The Vehicle ECU transmitted vehicle data, and both the Dashboard ECU and Logger ECU received the same traffic at the same time. The Logger stored the frames in `can_log.csv`, while the Dashboard decoded and displayed the values.

The Dashboard also demonstrated filtering. Its code provides separate filter sets for `all`, `speed`, and `rpm`, allowing the application to receive only the CAN IDs required for a particular operation.

---

## 3. CAN Message Definitions (Task 3)

| Signal              | CAN ID | Bytes | Range        | Encoding                          |
|----------------------|--------|-------|--------------|------------------------------------|
| Vehicle Speed        | 0x100  | 1     | 0–120 km/h   | raw byte = km/h                    |
| Engine RPM           | 0x101  | 2     | 800–5000 rpm | big-endian uint16 = rpm            |
| Coolant Temperature  | 0x102  | 1     | 20–120 °C    | raw byte = °C                      |

The Vehicle ECU generates the three values and transmits them as separate CAN frames. The RPM value is encoded using two bytes in big-endian form, while Speed and Temperature use one byte each. The values are updated continuously using the Vehicle ECU's transmission loop.

---

## 4. Learning Challenges — Results

### Challenge 1: Traffic Observation

The Vehicle ECU, Dashboard ECU and Logger ECU were run at the same time.

**Observation:** Both the Dashboard and Logger received identical traffic simultaneously. The Dashboard continuously displayed Speed, RPM and Temperature values, while the Logger recorded the incoming frames in the CSV file.

This demonstrated that multiple applications can listen to the same SocketCAN interface at the same time. A frame transmitted on the CAN interface can therefore be received by multiple sockets according to their filters.

**Result:** Successful. Simultaneous reception and logging worked correctly.

### Challenge 2: Message Filtering

The Dashboard was tested with the following filter modes:

```bash
python3 dashboard_ecu.py --filter speed
python3 dashboard_ecu.py --filter rpm
python3 dashboard_ecu.py --filter all
```

**Observation:**

- With `--filter speed`, only Speed values were updated. RPM and Temperature remained `--`.
- With `--filter rpm`, only RPM values were updated. Speed and Temperature remained `--`.
- With `--filter all`, all three vehicle parameters were displayed normally.

The filtering is implemented using CAN filters with `can_id` and `can_mask`. This allows the Dashboard to select the CAN IDs it is interested in.

**Result:** Successful. Message filtering worked as expected.

### Challenge 3: Unknown Message Detection

An undefined CAN message was manually injected using:

```bash
cansend vcan0 200#AABBCCDD
```

CAN ID `0x200` was not one of the three application message IDs (`0x100`, `0x101`, `0x102`).

**Observation:** The Logger recorded a new entry with CAN ID `0x200` in `can_log.csv`. This showed that the Logger records CAN traffic rather than only the predefined application messages.

The Dashboard code also contains an unknown-message handling path. If an unfiltered unknown frame reaches the Dashboard, it can report the CAN ID and payload instead of treating it as Speed, RPM or Temperature.

**Result:** Successful. The unknown message was successfully injected and recorded by the Logger.

### Challenge 4: Transmission Rate Study

The Vehicle ECU was restarted with a shorter transmission interval:

```bash
python3 vehicle_ecu.py --interval 0.05
```

The normal interval is 1 second, while `0.05` seconds means that the ECU attempts transmission approximately every 50 ms. Since the Vehicle ECU sends three CAN frames in each loop, this produces a much higher traffic rate than normal operation.

The system resource usage was checked using:

```bash
top
```

**Observation:**

- The transmission rate visibly increased when the interval was changed to `0.05` seconds.
- The CAN log grew much faster than during normal 1-second operation.
- The observed CPU usage was approximately **0.7%** in the `top` observation.
- The Dashboard continued to receive and display the messages.

The log file contained **4752 lines** when checked using:

```bash
wc -l logs/can_log.csv
```

This is the accumulated log count at the time of measurement, so it should not be interpreted as the number generated only during the fast-rate test.

**Result:** Successful. Increasing the transmission frequency increased CAN traffic and caused the log to grow faster, while the system continued operating normally.

### Challenge 5: Node Failure Study

The Vehicle ECU was stopped using `Ctrl+C` while the Dashboard ECU and Logger ECU were left running.

**Observation:** After approximately the configured 5-second timeout, the Dashboard displayed:

```text
WARNING: Vehicle ECU Offline
```

The Logger remained running but stopped receiving new CAN frames because the Vehicle ECU was no longer transmitting.

This demonstrates an important practical point: simply losing a transmitting application does not automatically create an application-level "Vehicle ECU Offline" message. The Dashboard detects the problem by monitoring how long it has been since the last Speed message was received.

**Result:** Successful. The Dashboard detected the Vehicle ECU failure using a timeout mechanism.

### Challenge 6: CAN FD Exploration

All three applications were restarted using the CAN FD option:

```bash
python3 vehicle_ecu.py --fd
python3 dashboard_ecu.py --fd
python3 logger_ecu.py --fd
```

The `vcan0` interface was configured for the larger CAN FD MTU as required by the assignment.

**Observation:** CAN FD frames were transmitted and received successfully by the three nodes. The applications continued communicating through the same virtual CAN architecture.

The main software-side difference is that the messages are created/listened for with the CAN FD option enabled (`is_fd`/`fd`). In this particular demonstration, the application messages themselves remained small, but the CAN FD frame format provides support for larger payloads than Classical CAN.

**Result:** Successful. CAN FD communication worked correctly.

### Challenge 7: Basic Diagnostics

The Dashboard ECU contains a basic diagnostic mechanism.

It stores the time when the most recent Speed message was received. If no Speed message is received for more than the configured timeout, the Dashboard prints:

```text
WARNING: Vehicle ECU Offline
```

The default timeout is 5 seconds.

This diagnostic feature was verified during Challenge 5 by stopping the Vehicle ECU and observing the warning on the Dashboard.

**Result:** Successful. Basic ECU communication-loss detection was demonstrated.

---

## 5. Key Learnings and Conclusions

This assignment gave a practical understanding of how SocketCAN works in Linux. Instead of using physical automotive CAN hardware, a complete communication network was created using the `vcan0` virtual interface. The Vehicle ECU generated messages, while the Dashboard and Logger received the same CAN traffic independently. Seeing both applications receive the same messages at the same time made the broadcast nature of CAN much clearer than learning it only theoretically.

The experiments also showed that CAN communication is more than just sending and receiving fixed messages. Message IDs can be filtered, unknown messages can be detected, traffic rates can be changed, and communication failures can be identified at the application level. The filtering experiment showed how an application can listen only to the messages it needs, while the node failure experiment showed why a timeout or heartbeat mechanism is useful in an automotive system.

Another important learning was the benefit of software-first development. Using `vcan0` allowed the communication logic to be developed and tested without waiting for physical CAN hardware. The CAN FD experiment also showed that the same basic architecture can be extended to CAN FD communication. Overall, the assignment connected Linux networking concepts, Python programming and automotive CAN communication into one working system.

---

## 6. Overall Experimental Results

| Task / Challenge | Test Performed | Result |
|---|---|---|
| Task 1 | Studied SocketCAN and Linux CAN architecture | Successfully understood |
| Task 2 | Built/understood three-node SocketCAN architecture | Successfully demonstrated |
| Task 3 | Defined and decoded Speed, RPM and Temperature messages | Successfully demonstrated |
| Challenge 1 | Simultaneous Dashboard + Logger reception | Successful |
| Challenge 2 | Speed/RPM/All message filtering | Successful |
| Challenge 3 | Injected `0x200` unknown message | Logged successfully |
| Challenge 4 | Increased transmission rate to 0.05 s | Traffic rate increased; CPU observed ~0.7% |
| Challenge 5 | Stopped Vehicle ECU | Dashboard showed ECU Offline warning |
| Challenge 6 | Enabled CAN FD on all nodes | CAN FD frames transmitted successfully |
| Challenge 7 | Tested Dashboard timeout diagnostics | Offline warning worked correctly |

---

## 7. Final Conclusion

The SocketCAN assignment was successfully completed using a software-only CAN network. The three-node system demonstrated the complete flow of automotive communication: a Vehicle ECU generated CAN messages, the Dashboard ECU processed and displayed them, and the Logger ECU recorded the traffic.

The practical experiments confirmed important SocketCAN concepts including shared CAN traffic, socket-level filtering, unknown message handling, transmission-rate effects, application-level diagnostics and CAN FD support. The successful use of `vcan0` also demonstrated that a significant portion of automotive communication software can be developed and tested before connecting real CAN hardware.

The final system therefore provides a useful small-scale demonstration of how Linux SocketCAN can be used as a foundation for automotive communication applications.

---
