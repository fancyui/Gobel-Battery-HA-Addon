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
