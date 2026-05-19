# Changelog


---------------

  存在的一个隐患

  ACK 的 CRC 未校验（jkbms_rs485.py:169-179）。_validate_ack_at() 只检查了功能码是否为 0x10
  和寄存器地址是否合法，没有验证 ACK 的 CRC16。如果 RS485 总线上发生 bit 翻转导致 ack[0] 的 pack_id
  字节损坏，理论上可能把 pack2 的帧错误归属到 pack1。但差分信号的 RS485 抗噪能力很强，且帧体 300
  字节也要同时有效，实际发生概率极低。

  另一个小问题

  主动查询备选路径（jkbms_rs485.py:926）中 slave_address 硬编码为 0x01，如果 setup 帧没被被动捕获到，主动查询只会请求
  pack1，pack2 的 setup 数据会缺失。但这不会导致数据错乱，只是 pack2 缺少配置参数。


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

