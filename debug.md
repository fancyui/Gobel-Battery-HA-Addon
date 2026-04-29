---
description: 
---

s6-rc: info: service s6rc-oneshot-runner: starting
s6-rc: info: service s6rc-oneshot-runner successfully started
s6-rc: info: service fix-attrs: starting
s6-rc: info: service fix-attrs successfully started
s6-rc: info: service legacy-cont-init: starting
s6-rc: info: service legacy-cont-init successfully started
s6-rc: info: service legacy-services: starting
s6-rc: info: service legacy-services successfully started
Gobel Power BMS Monitor Starting...
Loading options.json
2026-04-29 15:20:23,730 - __main__ - INFO - interface: wifi
2026-04-29 15:20:23,730 - __main__ - INFO - serial_port: /dev/ttyUSB0
2026-04-29 15:20:23,730 - __main__ - INFO - baud_rate: 115200
2026-04-29 15:20:23,730 - __main__ - INFO - ethernet_ip: 192.168.0.64
2026-04-29 15:20:23,730 - __main__ - INFO - ethernet_port: 8899
2026-04-29 15:20:23,730 - ha_mqtt - INFO - Connecting to MQTT broker at homeassistant.local:1883
2026-04-29 15:20:23,734 - ha_mqtt - INFO - Connected to MQTT broker successfully
2026-04-29 15:20:23,734 - bms_comm - INFO - Trying to connect BMS over 192.168.0.64:8899
2026-04-29 15:20:23,743 - bms_comm - INFO - Connected to BMS over Ethernet: 192.168.0.64:8899
2026-04-29 15:20:23,743 - bms_comm - INFO - Trying to connect BMS over 192.168.0.64:8899
2026-04-29 15:20:23,746 - bms_comm - INFO - Connected to BMS over Ethernet: 192.168.0.64:8899
2026-04-29 15:20:23,746 - __main__ - INFO - JK_PB BMS Monitor Working...
2026-04-29 15:20:23,746 - __main__ - INFO - JK_PB BMS RS485 Working...
2026-04-29 15:20:45,004 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:20:53,516 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:20:53,516 - jkbms_rs485 - WARNING - Failed to get dynamic data, retrying once...
2026-04-29 15:20:57,524 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:20:57,524 - jkbms_rs485 - ERROR - Failed to get dynamic data after retry
2026-04-29 15:21:01,031 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:21:01,031 - jkbms_rs485 - WARNING - Failed to get dynamic data, retrying once...
2026-04-29 15:21:05,037 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:21:05,037 - jkbms_rs485 - ERROR - Failed to get dynamic data after retry
2026-04-29 15:21:08,544 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:21:08,544 - jkbms_rs485 - WARNING - Failed to get dynamic data, retrying once...
2026-04-29 15:21:12,551 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:21:12,552 - jkbms_rs485 - ERROR - Failed to get dynamic data after retry
2026-04-29 15:21:16,059 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:21:16,059 - jkbms_rs485 - WARNING - Failed to get dynamic data, retrying once...
2026-04-29 15:21:20,065 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:21:20,066 - jkbms_rs485 - ERROR - Failed to get dynamic data after retry
2026-04-29 15:21:23,572 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:21:23,573 - jkbms_rs485 - WARNING - Failed to get dynamic data, retrying once...  收不到数据？能不能把收到的所有数据都打印出来



[2026-04-29 14:57:44.504]# RECV HEX/11 <<<
0C 10 16 20 00 01 02 00 00 8E 61 

[2026-04-29 14:57:44.709]# RECV HEX/11 <<<
0C 10 16 1E 00 01 02 00 00 8A BF 

[2026-04-29 14:57:44.929]# RECV HEX/11 <<<
0D 10 16 20 00 01 02 00 00 83 F1 

[2026-04-29 14:57:45.148]# RECV HEX/11 <<<
0D 10 16 1E 00 01 02 00 00 87 2F 

[2026-04-29 14:57:45.388]# RECV HEX/11 <<<
0E 10 16 20 00 01 02 00 00 97 01 

[2026-04-29 14:57:45.590]# RECV HEX/11 <<<
0E 10 16 1E 00 01 02 00 00 93 DF 

[2026-04-29 14:57:45.812]# RECV HEX/11 <<<
0F 10 16 20 00 01 02 00 00 9A 91 

[2026-04-29 14:57:46.031]# RECV HEX/11 <<<
0F 10 16 1E 00 01 02 00 00 9E 4F 

[2026-04-29 14:57:46.281]# RECV HEX/308 <<<
55 AA EB 90 02 00 DA 0C D9 0C D9 0C D7 0C BA 0C D7 0C D7 0C D6 0C BD 0C D9 0C D7 0C D9 0C D9 0C D9 0C D9 0C D9 0C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF 00 00 D5 0C 20 00 00 04 49 00 46 00 47 00 44 00 48 00 46 00 4C 00 49 00 49 00 46 00 49 00 46 00 4E 00 4C 00 4A 00 48 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 01 00 00 00 00 4C CD 00 00 00 00 00 00 00 00 00 00 FE 00 FD 00 00 00 08 00 00 00 00 61 27 7C 01 00 A0 86 01 00 00 00 00 00 5F 01 00 00 64 00 00 00 99 E6 16 00 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF 00 01 00 00 00 67 27 00 00 00 00 71 49 3D 40 00 00 00 00 87 14 00 00 00 01 01 01 00 01 01 00 B2 73 19 00 00 00 00 00 04 01 FE 00 FD 00 59 27 69 3B E6 0B 6E 00 00 00 53 25 00 00 00 00 02 01 00 00 00 00 00 00 00 00 00 FE FF 7F DC 2F 01 01 B0 0F 07 00 00 A9 00 10 16 20 00 01 05 9A 

[2026-04-29 14:57:46.500]# RECV HEX/308 <<<
55 AA EB 90 01 00 D4 0D 00 00 C4 09 00 00 54 0B 00 00 42 0E 00 00 48 0D 00 00 0A 00 00 00 75 0D 00 00 8C 0A 00 00 7A 0D 00 00 48 0D 00 00 BA 09 00 00 30 75 00 00 03 00 00 00 3C 00 00 00 A0 86 01 00 2C 01 00 00 46 00 00 00 1E 00 00 00 E8 03 00 00 58 02 00 00 26 02 00 00 58 02 00 00 26 02 00 00 00 00 00 00 32 00 00 00 20 03 00 00 BC 02 00 00 10 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 A0 86 01 00 05 00 00 00 E4 0C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 A1 07 00 50 12 3C 32 18 FE FF FF FF 9F E9 6D 02 00 00 00 00 5D 00 10 16 1E 00 01 64 56 

[2026-04-29 14:57:46.689]# RECV HEX/11 <<<
01 10 16 20 00 01 02 00 00 D6 F1 

[2026-04-29 14:57:46.910]# RECV HEX/11 <<<
01 10 16 1E 00 01 02 00 00 D2 2F 




Sensors
Pack 01 Cell Voltage 01
3,540 mV
Pack 01 Cell Voltage 02
Unknown
Pack 01 Cell Voltage 03
Unknown
Pack 01 Cell Voltage 04
Unknown
Pack 01 Cell Voltage 05
Unknown
Pack 01 Cell Voltage 06
Unknown
Pack 01 Cell Voltage 07
Unknown
Pack 01 Cell Voltage 08
Unknown
Pack 01 Cell Voltage 09
Unknown
Pack 01 Cell Voltage 10
Unknown
Pack 01 Cell Voltage 11
Unknown
Pack 01 Cell Voltage 12
Unknown
Pack 01 Cell Voltage 13
Unknown
Pack 01 Cell Voltage 14
Unknown
Pack 01 Cell Voltage 15
Unknown
Pack 01 Cell Voltage 16
Unknown
Pack 01 Cell Voltage Diff
0 mV
Pack 01 Cell Voltage Max
3,540 mV
Pack 01 Cell Voltage Max Index
1
Pack 01 Cell Voltage Min
3,540 mV
Pack 01 Cell Voltage Min Index
1
Pack 01 Cell Voltage Warning 01
normal
Pack 01 Cell Voltage Warning 02
Unknown
Pack 01 Cell Voltage Warning 03
Unknown
Pack 01 Cell Voltage Warning 04
Unknown
Pack 01 Cell Voltage Warning 05
Unknown
Pack 01 Cell Voltage Warning 06
Unknown
Pack 01 Cell Voltage Warning 07
Unknown
Pack 01 Cell Voltage Warning 08
Unknown
Pack 01 Cell Voltage Warning 09
Unknown
Pack 01 Cell Voltage Warning 10
Unknown
Pack 01 Cell Voltage Warning 11
Unknown
Pack 01 Cell Voltage Warning 12
Unknown
Pack 01 Cell Voltage Warning 13
Unknown
Pack 01 Cell Voltage Warning 14
Unknown
Pack 01 Cell Voltage Warning 15
Unknown
Pack 01 Cell Voltage Warning 16
Unknown
Pack 01 Fault Cell
Off
Pack 01 Fault Charge MOS
Off
Pack 01 Fault Discharge MOS
Off
Pack 01 Fault NTC
Off
Pack 01 Fault Sampling
Off
Pack 01 Hardware Version
Pack 01 Protect High Cell Voltage
Off
Pack 01 Protect High Charge Current
Off
Pack 01 Protect High Discharge Current
Off
Pack 01 Protect High Total Voltage
Off
Pack 01 Protect Low Cell Voltage
Off
Pack 01 Protect Low Total Voltage
Off
Pack 01 Protect Short Circuit
Off
Pack 01 Software Version
Pack 01 Temperature 01
0.0 °C
Pack 01 Temperature 02
0.0 °C
Pack 01 Temperature 03
0.0 °C
Pack 01 Temperature 04
0.0 °C
Pack 01 Temperature 05
0.0 °C
Pack 01 View Balance Current
0.00 A
Pack 01 View Current
0.00 A
Pack 01 View Cycle Number
0 cycles
Pack 01 View Design Capacity
0.0 Ah
Pack 01 View Energy Charged
0 Wh
Pack 01 View Energy Discharged
0 Wh
Pack 01 View Full Capacity
0.0 Ah
Pack 01 View Num Cells
1 cells
Pack 01 View Num Temps
5 NTCs
Pack 01 View Remain Capacity
0.0 Ah
Pack 01 View SOC
0.0%
Pack 01 View SOH
0.0%
Pack 01 View Voltage
0 V
Total Current
0.00 A
Total Full Capacity
0.0 Ah
Total Packs Num
1 packs
Total Remain Capacity
0.0 Ah
Total SOC
0%
Logbook

2026-04-29 15:51:25,125 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 66 bytes
2026-04-29 15:51:27,762 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 132 bytes
2026-04-29 15:51:27,762 - jkbms_rs485 - WARNING - No valid dynamic 55AA frame received after waiting
2026-04-29 15:51:27,763 - jkbms_rs485 - WARNING - Failed to get dynamic data, retrying once...
2026-04-29 15:51:29,303 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 77 bytes
2026-04-29 15:51:31,943 - jkbms_rs485 - INFO - receive_55aa_frames: extracted 2 55AA frame(s) from 726 bytes
2026-04-29 15:51:33,043 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 55 bytes
2026-04-29 15:51:36,343 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 55 bytes
2026-04-29 15:51:38,983 - jkbms_rs485 - INFO - receive_55aa_frames: extracted 2 55AA frame(s) from 726 bytes
2026-04-29 15:51:45,145 - jkbms_rs485 - INFO - receive_55aa_frames: extracted 2 55AA frame(s) from 902 bytes
2026-04-29 15:51:46,243 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 55 bytes
2026-04-29 15:51:49,544 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 55 bytes
2026-04-29 15:51:52,184 - jkbms_rs485 - INFO - receive_55aa_frames: extracted 2 55AA frame(s) from 726 bytes
2026-04-29 15:51:58,344 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 308 bytes
2026-04-29 15:52:00,984 - jkbms_rs485 - INFO - receive_55aa_frames: extracted 2 55AA frame(s) from 726 bytes
2026-04-29 15:52:02,084 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 55 bytes
2026-04-29 15:52:05,384 - jkbms_rs485 - WARNING - receive_55aa_frames: NO 55AA frame found in 55 bytes