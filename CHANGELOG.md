---
description: 
---

# Changelog


## 1.9.78

-   [JKBMS] Fix 'Serial' object has no attribute 'gettimeout' AttributeError when connecting the BMS over a serial port in passive listening mode.

---------------


## 1.9.77

-   [PACE232] Implement robust structural validation for packet type classification. Distinguishes analog and warning packets by validating their schema structure for the reported number of parallel packs, automatically adapting to varying firmware data lengths (user-defined fields size U and warning status bytes W). This resolves protocol desync, cell voltage, temperature, and SOC telemetry corruption in multi-pack configurations.
-   [PACE/TDT] Fix IndexError parsing crashes on firmware versions without active balancing support by implementing safe boundary checks.
-   [PACE/TDT] Correct active balancing status byte offsets across PACE RS232, RS485, and TDT RS232 protocols.
-   [Dashboard] Add active and passive balancing status sensors to the PACE/TDT BMS pack details grid layout in the HA dashboard. Correct entity case mismatch (from uppercase SOC/SOH to lowercase soc/soh) to align with Home Assistant's automatically registered lowercase MQTT entity IDs.

---------------


## 1.9.74

-   [PACE/TDT] Separate Passive and Active Balancing Status into distinct sensors:
    *   **Passive Balancing Status**:
        *   Keys: `balancing_status_passive_1`, `balancing_status_passive_2`
        *   HA discovery name: `Pack 0x Balancing Status Passive 1 / 2`
        *   Value: Raw bitmask bypass-resistor active byte values (multiple bits can be 1).
    *   **Active Balancing Status**:
        *   Keys: `balancing_status_active_1`, `balancing_status_active_2`
        *   HA discovery name: `Pack 0x Balancing Status Active 1 / 2`
        *   Value: Decoded cell index (1-8, 9-16). Returns 0 when active balancing is inactive.
-   [TDT] Fix ValueError crash when balance state values are greater than 1.

---------------


## 1.9.73

-   [PACE/TDT] Add raw ASCII and Hexadecimal packet logging for all telemetry send and receive operations when `debug` configuration is enabled.
-   [PACE/TDT] Fix method signatures for capacity and product info methods.

---------------


## 1.9.72

-   [PACE/TDT] Expose active balancing status (`balance_state_1` and `balance_state_2`) sensors for PACE (RS232, RS485, WiFi) and TDT BMS protocols.
-   [BMS] Standardize debug logging format for parsed analog and warning telemetry across JK, PACE, and TDT BMS drivers.

---------------


## 1.9.71

-   [PACE485] Fix cell temperature sensors unit (from '℃' to standard '°C') so Home Assistant accepts the sensors.

---------------


## 1.9.70

-   [PACE232] Dynamically determine user-defined fields and warning status bytes parsing lengths to support differing battery pack firmware versions.
-   [PACE232] Implement a ratiometric packet classification method to differentiate Analog and Warning response packets. Delayed/out-of-order packets are salvaged, parsed, and cached to prevent Home Assistant sensor state corruption.

---------------


## 1.9.66

-   [Addon] Add multilingual translation support (English, Germany and Chinese) for configuration options to display user-friendly names and descriptions in the Home Assistant Add-on settings page.

---------------


## 1.9.61

-   [JKBMS] Add `jk_display_index_start` configuration setting with choices "00" or "01" (default) to allow matching the Home Assistant entity and pack labels with the physical dial-up address of the battery pack.

---------------


## 1.9.60

-   [JKBMS] Refactor JK BMS serial reader into an asynchronous background listener thread to completely prevent serial port blocking in the main loop. Non-55AA frames (like Modbus master queries) are automatically filtered and discarded. Main publishing logic fetches telemetry from thread-safe caches with 0.0s latency, resolving HA entity and pack count fluctuations.

---------------


## 1.9.59

-   [JKBMS] Make dynamic telemetry cache expiration adaptive based on the refresh interval (`max(30s, refresh_interval * 3)`) to support larger refresh interval settings (e.g. 20s) without false-offline reports.

---------------


## 1.9.58

-   [JKBMS] Optimize passive read loop by increasing reading timeout to 8.0s (fully covering the observed 7.0s cycle time for 16 packs) and adding a 5-second freshness cache bypass to prevent double reading from blocking the serial port.

---------------


## 1.9.57

-   [JKBMS] Further increase passive reading timeout window from 2.0s to 4.0s to guarantee a full 3.2-second sequential polling cycle of 16 packs is captured.

---------------


## 1.9.56

-   [JKBMS] Increase passive reading timeout window from 1.0s to 2.0s to reliably capture telemetry frames from up to 16 parallel battery packs.

---------------


## 1.9.55

-   [JKBMS] Cache dynamic telemetry frames for up to 30 seconds to prevent pack count (total_packs_num) and battery entities from fluctuating due to temporary packet drops or serial read timeouts.

---------------


## 1.9.54

-   [JKBMS] Map Modbus Slave ID directly as pack ID to support 0-based communication address configurations (addresses 0, 1, 2, 3...) and resolve pack mapping conflicts in Home Assistant.

---------------


## 1.9.53

-   [JKBMS] Map 1-based Modbus Slave ID in trailing ACK to 0-based pack ID to fix missing Pack 01 and prevent duplicate/misaligned pack devices in HA.

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