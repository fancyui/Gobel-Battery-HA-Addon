---
description: 
---

# Changelog


---------------


## 1.9.52

-   [PACEWIFI] Add support for PACE_LV_WIFI bms_type to passively parse telemetry data actively broadcasted over WiFi.

---------------


## 1.9.50

-   [JKBMS] Dynamically parse Modbus ACK at the end of frames, making data parsing independent of specific packet lengths.

---------------


## 1.9.48

-   [JKBMS] Fixed pack identification logic to prevent data collision between different packs.
-   [JKBMS] Send each pack's sensor data to its own separate Home Assistant device.

---------------


## 1.9.46

-   [JKBMS] Changed verbose frame-parsing log messages from WARNING to DEBUG to reduce log noise.

---------------


## 1.9.45

-   [JKBMS] Refined multi-pack integration and setup configuration parameters (Reg=0x161E).
-   [PACE232] Added heating film status (status_heating) to instruction_state.

---------------

## 1.9.21

-   Add build.yaml to fix Docker build failure (missing BUILD_FROM arg).


---------------

## 1.9.20

-   Add JK BMS RS485 support.
-   Fix Energy Discharged/Charged bug.


---------------

## 1.9.0

-   Auto reconnection after connection lost.
-   Add index of max/min cell voltage.
-   Modify Protoss PW10 / Waveshare manual, change 'Flow Control Settings' to 'Flow Control', 'Software Flow Control' to 'OFF'.


---------------

## 1.8.2

-   Fix temperature unit error.
-   Fix max/min voltage unit error.
-   Add voltage difference value.
-   Change data reading timeout to 3 seconds.

---------------


## 1.8.0

-   Value precision of energy charged/discharged is changed to 5.

---------------


## 1.7.8

-   TDT BMS bug fix.

---------------


## 1.7

-   fix RS232 multiple packs bug.
    for Pace BMS, use PACE_LV (latest version protocol) by default, if it does not work, try PACE_LV_V1.
-   add max/min cell voltage for whole system and each pack.
-   add TDT BMS support.

---------------