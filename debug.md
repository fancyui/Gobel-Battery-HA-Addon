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