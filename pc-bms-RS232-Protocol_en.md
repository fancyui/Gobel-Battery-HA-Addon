# PACEex Peicheng Electronics

Classification: Internal
Document Number: PC-SD-TS-034
Version: V3.1

---

## RS232 Communication Protocol

### Protocol Number: HS001-PC-232-BP-UN-DATA-V3.1

## Peicheng Electronic Technology Co., Ltd.

| Prepared by: Ouyang Liming | Effective Date: 2023-09-19 |
| -------------- | -------------------- |
| Reviewed by: Zheng Xuhui | Approved by: Gong Weigang |

---

Peicheng Electronic Technology Co., Ltd. holds the copyright and other exclusive rights to this document. Without written permission, this document (in whole or in part) shall not be disclosed to any third party or used after modification.

---

## Revision Record

| Date | Change Content | Responsible Person/Version |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 2018-07-05 | Initial compilation and finalization | Wang Yongxiang |
| 2022-03-02 | Added inverter protocol commands C5 and C6. | Liu Ning |
| 2022-05-07 | Changed inverter protocol commands from C5, C6 to EB, EC. | Liu Ning |
| 2022-05-25 | Removed protocol matching reporting function before communication; added inverter protocol byte frame compatibility at the end of the 44H command to resolve false error reporting during parallel operation. | Liu Ning |
| 2022-06-13 | Increased RS232 parallel unit count to 32. | Liu Ning |
| 2022-08-20 | Added inverter protocol macro definition comparison table; host computer is not allowed to arbitrarily modify macros corresponding to the protocol; lower computer must write software strictly according to macro values. | Liu Ning |
| 2022-10-20 | Added description for C6 command. | Liu Ning |
| 2022-11-14 | Added recoverable parameter selection option byte to upgrade command. | Liu Ning |
| 2022-11-16 | Added host computer test tool read/write mod information commands, 7EH, 7FH. | Liu Ning |
| 2022-11-17 | Supplemented inverter protocol macro definition comparison table; existing definitions should not be altered; new additions should be appended. | Liu Ning |
| 2022-11-18 | Added N maximum 128 within 7EH, 7FH. | Liu Ning |
| 2022-12-03 | Added Pack Soh, Independent Total Voltage 1 and Independent Current 1 after 42H; added Authentication Fault 1 after 44H. | Liu Ning |
| 2022-12-04 | Added definitions for several bits within Authentication Fault 1; also corrected user-defined count P = 9. | Liu Ning |
| 2022-12-15 | Supplemented inverter protocol macro definition comparison table; existing definitions should not be altered; new additions should be appended. | HS-PACE-232-BP-V2.0 |
| 2022-12-16 | Added function for BIT3 in the table for Authentication Fault 1. | HS-PACE-232-BP-V2.0 |
| 2022-12-17 | Changed Authentication Fault 1 to Fault Status 8 and updated Fault Status 8 content. | HS-PACE-232-BP-V2.1 |
| 2022-12-18 | Added current limiting fault flag to Fault Status 5-BIT6. | |
| 2022-12-19 | Added CID2 (60H*63H) for protocol selection. | |
| 2023-02-22 | 1. Added COMMAND_INFO_04H, 05H in control command 99H to coordinate with BIT6 (System Lock/Battery Pack Lock) of Fault Status 8. | Liu Ning |
| 2023-04-20 | Added static balance enable and disable control switch. | HS-PACE-232-BP-V2.3 |
| 2023-05-15 | Added summary capacity after 42H. | HS-PACE-232-BP-V2.4 |
| 2023-05-20 | Added Bluetooth device name information in CHI command. | HS-PACE-232-BP-V2.5 |
| 2023-06-28 | Added Bluetooth information display 64H. | HS-PACE-232-BP-V2.5 |
| 2023-08-16 | Control Status 4.BIT6 defined as system lock function flag.<br />Fault Status 5.BIT3 defined as communication fault flag. | HS-PACE-232-BP-V2.6 |
| 2023-09-07 | 1. Added network SN information read/write function (64H, 65H, 66H).<br />Added crystal oscillator abnormal data upload (80H). | HS-PC-232-BP-V2.7, Liu Ning |
| 2023-09-19 | 1. Fault Status 8_BIT7 defined as MCI overvoltage fault.<br />Added Indicator Status 9 after 44H. | HS-PC-232-BP-V2.8, Ouyang Liming |
| 2023-10-11 | 1. Added protocol transparent transmission command (67H). | HS-PC-232-BP-V2.9, Ouyang Liming |
| 2023-10-20 | 1. Added DOH~DPH as user-defined commands in control instructions. | HS-PC-232-BP-V2.9, Ouyang Liming |
| 2024-04-29 | 1. Added active balance function enable/disable control (6AH).<br />Added active balance function status read (68H).<br />Added L/16 string active balance status report (44H). | HS001-PC-232-BP-UN-DATA-V3.0, Wang Anning |
| 2024-06-17 | 1. Added Fault Status 10 to alarm quantity (44H), new 12V fault.<br />Added Fault Status 8, Fault Status 10, important status save to read historical record (MH). | HS001-PC-232-BP-UN-DATA-V3.1, Ouyang Liming |

---

## 1. Physical Interface and Communication Method

### 1.1. Physical Interface

The physical interface shall use a serial communication port, employing the standard RS232 method. The information transmission method is asynchronous, with 1 start bit, 8 data bits, 1 stop bit, and no parity bit. The data transmission rate is 9600 bps.

#### 1.2. Communication Method

The communication method adopts a master-slave response mode. The PC software or monitoring device acts as the master to initiate communication commands, and the BMS acts as the slave to return response information. The master sends a communication command; if no response is received from the slave within 500ms or the received response information is erroneous, the communication process is considered failed.

## 2. Basic Format of the Protocol

### 2.1. Basic Format of Frame Structure

**Table A.1 Frame Structure**

| Sequence No. | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| ----------- | --- | --- | --- | ---- | ---- | ------ | ------ | ------ | --- |
| Byte Count | 1 | 1 | 1 | 1 | 1 | 2 | LEND/2 | 2 | 1 |
| ASCII Byte Count | 1 | 2 | 2 | 2 | 2 | 4 | LEND | 4 | 1 |
| Format | SOI | VER | ADR | CID1 | CID2 | LENGTH | INFO | CHKSUM | EOI |

### 2.2. Explanation of Basic Format

**Table A.2 Basic Format**

| Seq. No. | Symbol | Meaning | Note |
| ---- | ------ | ----------------------------------------------------------------------- | --------- |
| 1 | SOI | Start of Information | (7EH) |
| 2 | VER | Communication Protocol Version (V2.5) | (25H) |
| 3 | ADR | Address description for different devices of the same type (0-15) | |
| 4 | CID1 | Device Identification Code (device type description) | |
| 5 | CID2 | Command Info: Control Identification Code (data or action type description)<br />Response Info: Return Code RTN | |
| 6 | LENGTH | INFO byte length (including LEND and LCHKSUM) | |
| 7    | INFO   | Command Information: Control Data Information COMMAND_INFO<br />Response Information: Response Data Information DATA_INFO |           |
| 8    | CHKSUM | Checksum Code                                                                |           |
| 9    | EOI    | End Code (END OF INFORMATION)                                            | CR (00H) |

> Note:
>
> - VER- Indicates the communication protocol version, fixed as V2.5, i.e., 25H.
> - ADR- Indicates the battery PACK address. The BMS uses a four-bit DIP switch for address setting, with an address range of 0~15.

---

### 2.3. Data Format

**2.3.1. Basic Data Format**

Except for SOI and EOI, which are interpreted and transmitted in hexadecimal, all other items are interpreted in hexadecimal but transmitted in hexadecimal-ASCII code format. Each byte is represented by two ASCII codes. For example, when CID2 = 4BH, the two bytes transmitted are 34H (ASCII code for "4") and 42H (ASCII code for "B").

**2.3.2. LENGTH Data Format**

**Table A.3 LENGTH Data Format**

| High Byte         | Low Byte                                     |
| -------------- | ------------------------------------------ |
| Checksum LCHKSUM | LENID (Indicates the number of ASCII code bytes transmitted for INFO) |
| D15            | D14                                        |

**2.3.3. LENID**

LENID represents the number of ASCII code bytes for the INFO item. When LENID = 0, INFO is empty, meaning this item does not exist. Since LENID is only 12 bits, the maximum data packet size must not exceed 4095 bytes.

In transmission, LENGTH sends the high byte first, then the low byte, transmitted as four ASCII codes.

**2.3.4. LCHKSUM**

Calculation of the checksum LCHKSUM: D11D10D9B8 + D7D6D5D4 + D8B2D1D0

After summation, take the modulo 16 remainder, invert it, and add 1.

For example:

The number of ASCII code bytes in INFO is 18, i.e., LENID = 0000 0001 0010B.

D11D10D9B8 + D7D6D5D4 + D8B2D1D0 = 0000B + 0001B + 0010B = 0011B. The modulo 16 remainder is 0011B. Inverting 0011B and adding 1 gives 1101B, so LCHKSUM is 1101B.

Thus: LENGTH is 1101 0000 0001 0010B, i.e., D012H.

**2.4. CHKSUM Data Format**

The calculation of CHKSUM involves summing the ASCII code values of all characters except SOI, EOI, and CHKSUM. Take the modulo 65536 remainder of the result, invert it, and add 1.

For example:

The received or transmitted character sequence is:

"‘1203400356ABCEFFC72’R" ("‘" is SOI, "CR" is EOI),

Then the FC72 in the last 5 characters "FC72’R" is CHKSUM.

The calculation method is:

‘1’ + ‘2’ + ‘0’ + … + ‘F’ + ‘E’ = 31H + 32H + 30H + … + 46H + 45H = 038EH

038EH modulo 65536 remainder is 038EH. Inverting 038EH and adding 1 gives FC72H.

**2.5. DATA_INFO Data Format**

Analog data transmission adopts two forms: fixed-point numbers and floating-point numbers, either can be chosen. This protocol uniformly uses fixed-point numbers for data transmission.

1) **Integer Data Format (INTEGER, 2 bytes)**

   - Signed integer -32768 to +32767
   - Unsigned integer 0 to +65535
   - Transmission order is high byte first, then low byte.
2) **Unsigned Character Type (CHAR, 1 byte, 0 - 255)**

**Table A.4 Fixed-Point Number Data Types**

| No. | Telemetry Content           | Data Type     | Transmission Unit | Explanation                                                                                                                                                       |
| ---- | ------------------ | ---------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Battery Cell Voltage       | Unsigned Integer | mV       |                                                                                                                                                            |
| 2    | Temperature               | Unsigned Integer | 0.1K     | Temperature calculation is as follows:<br />In response information, the unit for temperature data is 0.1K.<br />e.g.: 25.5℃ = (25.5 + 273) * 10 = 2985 (0.1K)<br />-12.4℃ = (-12.4 + 273) * 10 = 2606 (0.1K) |
| 3    | Battery Pack Total Voltage | Unsigned Integer | mV       |                                                                                                                                                            |
| 4    | Battery Pack Charge/Discharge Current | Signed Integer | 10mA     | Positive for charging, negative for discharging, represented in two's complement                                                                                                                               |
| 5    | Battery Pack Capacity       | Unsigned Integer | 10mAH    | Includes remaining capacity, full charge capacity, design capacity                                                                                                                           |

**2.6. Date and Time**

DATA_TIME and COMMAND_TIME formats are shown in the table below:

**Table A.5 Date and Time Format**

| Name | Value Range | Data Type | Remarks                  |
| ---- | -------- | -------- | --------------------- |
| Year   | (0 - 99) | CHAR     | Character type, 1 byte, decimal |
| Month   | (1 - 12) | CHAR     | Character type, 1 byte, decimal |
| Day   | (1 - 31) | CHAR     | Character type, 1 byte, decimal |
| Hour   | (0 - 23) | CHAR     | Character type, 1 byte, decimal |
| Minute   | (0 - 59) | CHAR     | Character type, 1 byte, decimal |
| Second   | (0 - 59) | CHAR     | Character type, 1 byte, decimal |

> Note: The year is transmitted in string format. Actual value = transmitted value + 2000. Year range is 2000-2099.

## 3. Code Allocation

CID1 and CID2 code allocation tables are as follows:

### 3.1. Device Type Code Allocation Table (CID1)

CID1 code allocation table is shown below:

**Table A.6 CID1 Code Allocation Table**

| No. | Content     | CID1 | Remarks           |
| ---- | -------- | ---- | -------------- |
| 1    | LiFePO4 Battery | 46H  | (Applicable to NMC Lithium) |

---

### 3.2. Command Information Code Allocation Table (CID2)

CID2 code allocation table is shown below:

#### Table A.7 CID2 Code Allocation Table

| No. | Content                      | CID2 | Remarks     |
| ---- | ------------------------- | ---- | -------- |
| 1.   | Get PACK Analog Quantities          | 42H  |          |
| 2.   | Get PACK Alarm Quantities          | 44H  |          |
| 3.   | Read Inverter Protocol List Number    | 60H  |          |
| 4.   | Read Inverter Protocol List Name    | 61H  |          |
| 5.   | Read Current Inverter Protocol        | 62H  |          |
| 6.   | Set Current Inverter Protocol        | 63H  |          |
| 7.   | Read B35 Module Information         | 64H  |          |
| 8.   | Record B35 Module SN Information   | 65H  |          |
| 9.   | Get B35 Module SN Information     | 66H  |          |
| 10.  | Protocol Passthrough Command              | 67H  |          |
| 11.  | ……                      |      | Reserved for Home Storage |
| 12.  | Set Active Balancing Function          | 6AH  |          |
| 13.  | Get Active Balancing Status          | 6BH  |          |
| 14.  | ……                      |      | Reserved for Home Storage |
| 15.  | PC Test Tool Write MCU Information | 7EH  |          |
| 16.  | PC Test Tool Read MCU Information | 7FH  |          |
| 17.  | Get MCU Clock Source Configuration Information   | 80H  |          |
| 18.  | Get PACK Quantity            | 90H  |          |
| 19.  | Control Command                  | 99H  |          |
| 20.  | Charge MOSFET Control          | 9AH  |          |
| 21.  | Discharge MOSFET Control          | 9BH  |          |
| 22.  | Shutdown/Hibernation                 | 9CH  |          |
| 23.  | Read Cell Hibernation Parameters          | A0H  |          |
| 24.  | Read Historical Records              | A1H  |          |
| 25.  | Restore Default Parameters              | A4H  |          |
| 26.  | Set Capacity Release Percentage Parameter    | A5H  |          |
| 27.  | Get PACK Capacity Information        | A6H  |          |
| 28.  | Set PACK Capacity Information        | A7H  |          |
| 29.  | Set Cell Sleep Parameters          | A8H  |          |
| 30.  | Calibrate Reference Voltage              | A9H  |          |
| 31.  | Current Zero Point Calibration              | AAH  |          |
| 32.  | Calibrate Discharge Current              | ABH  |          |
| 33.  | Calibrate Charge Current              | ACH  |          |
| 34.  | Calibrate Total Voltage                | ADH  |          |
| 35.  | Set Full Charge Parameters & Capacity Alarm    | AEH  |          |
| 36.  | Read Full Charge Parameters & Capacity Alarm    | AFH  |          |
| 37.  | Get BMS Date and Time         | B1H  |          |
| 38.  | Set BMS Date and Time         | B2H  |          |
| 39.  | Clear Historical Records              | B3H  |          |
| 40.  | Set Number of Battery Strings              | B4H  |          |
| 41.  | Set Balancing Parameters              | B5H  |          |
| 42.  | Read Balancing Parameters              | B6H  |          |
| 43.  | Set Timed Storage Interval Time      | B7H  |          |
| 44.  | Read Timed Storage Interval Time      | B8H  |          |
| 45.  | Set Timed Storage Start Time      | B9H  |          |
| 46.  | Read Timed Storage Start Time      | BAH  |          |
| 47.  | Set Timed Storage End Time      | BBH  |          |
| 48.  | Read Timed Storage End Time      | BCH  |          |
| 49.  | Set Charge/Discharge Cycle Count        | BDH  |          |
| 50.  | Get Software Version Information          | C1H  |          |
| 51.  | Get Product Information              | C2H  |          |
| 52.  | Input BMS Product Information         | C3H  |          |
| 53.  | Input PACK Product Information        | C4H  |          |
| 54.  | Get Internal Version Information          | C6H  |          |
| 55.  | Set Cell Overcharge Parameters          | D0H  |          |
| 56.  | Read Cell Overcharge Parameters          | D1H  |          |
| 57.  | Set Cell Over-discharge Parameters          | D2H  |          |
| 58.  | Read Cell Over-discharge Parameters          | D3H  |          |
| 59.  | Set Overall Overcharge Parameters          | D4H  |          |
| 60.  | Read Overall Overcharge Parameters          | D5H  |          |
| 61.  | Set Overall Over-discharge Parameters          | D6H  |          |
| 62.  | Read Overall Over-discharge Parameters          | D7H  |          |
| 63.  | Set Charge Overcurrent Parameters          | D8H  |          |
| 64.  | Read Charge Overcurrent Parameters          | D9H  |          |
| 65.  | Set Discharge Overcurrent 1 Parameters       | DAH  |          |
| 66.  | Read Discharge Overcurrent 1 Parameters       | DBH  |          |
| 67.  | Set Battery High Temperature Parameters          | DCH  |          |
| 68.  | Read Battery High Temperature Parameters          | DDH  |          |
| 69.  | Set Battery Low Temperature Parameters          | DEH  |          |
| 70.  | Read Battery Low Temperature Parameters          | DFH  |          |
| 71.  | Set MOSFET High Temperature Parameters      | E0H  |          |
| 72.  | Read MOSFET High Temperature Parameters      | E1H  |          |
| 73.  | Set Discharge Overcurrent 2 Parameters       | E2H  |          |
| 74.  | Read Discharge Overcurrent 2 Parameters       | E3H  |          |
| 75.  | Set Short Circuit Delay Parameters          | E4H  |          |
| 76.  | Read Short Circuit Delay Parameters          | E5H  |          |
| 77.  | Set Ambient Temperature Parameters          | E6H  |          |
| 78.  | Read Ambient Temperature Parameters          | E7H  |          |
| 79.  | Get Current Limiting Parameters              | EDH  |          |
| 80.  | Set Current Limiting Parameters              | EEH  |          |
| 81.  | Read Inverter Protocol            | EBH  |          |
| 82.  | Set Inverter Protocol            | ECH  |          |
| 83.  | Enter Test Mode              | FFH  |          |

#### Table A.8 CID2 Response Code Table (RTN)

| Sequence Number | Meaning           | RTN             | Remarks   |
| ---- | -------------- | --------------- | ------ |
| 1    | Normal           | CID2 of request |        |
| 2    | Reserved           | 01H             |        |
| 3    | CHKSUM Error    | 02H             |        |
| 4    | LCHKSUM Error   | 03H             |        |
| 5    | CID2 Invalid      | 04H             |        |
| 6    | Reserved           | 05H             |        |
| 7    | Reserved           | 06H             |        |
| 8    | Operation or Write Error | 09H             | Custom |

## 4. Command Description

### 4.1. Get PACK Analog Values (42H)

#### Table A.9 Get PACK Analog Values Command Information

| Sequence Number   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 42H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is one byte, i.e., COMMAND:

- COMMAND = FFH, get all PACK analog values.
- COMMAND = 01H, get PACK1 analog values.
- ……
- COMMAND = 0FH, get PACK15 analog values.

Description: Applicable to RS232 interface with BMS address set to 1. Combined with RS485 using master-slave structure, multiple PACK data can be obtained; if the BMS address is not equal to 1 or RS485 is not in a master-slave structure, only the analog values of this PACK can be obtained, and COMMAND can be set to 01H or FFH.

#### Table A.10 Get PACK Analog Values Response Information

| Sequence Number   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: DATA_INFO consists of INFOFLAG and DATAI. DATAI details are shown in Table A.11.
INFOFLAG is 00H or 01H.

#### Table A.11 Analog Value DATAI Data Transmission Sequence

| Sequence Number  | Content                       | DATAI Byte Count | Remarks      |
| ----- | -------------------------- | ------------ | --------- |
| 1     | * PACK Quantity M / COMMAND Value | 1            |           |
| 2     | PACK 1 Battery Data            |              | See Table A.12 |
| 3     | ……                       | ……         |           |
| M + 1 | PACK M Battery Data            |              | See Table A.12 |

\* When COMMAND in the command is FFH, the response information is the PACK quantity; for other values, the response information is the value of COMMAND.

#### Table A.12 Single Battery Group Analog Value Content and Transmission Sequence

| Sequence Number       | Content                 | DATAI Byte Count | Remarks                                       |
| ---------- | -------------------- | ------------ | ------------------------------------------ |
| 1          | Number of Battery Cells M       | 1            |                                            |
| 2          | Battery Cell Voltage 1       | 2            |                                            |
| 3          | Battery Cell Voltage 2       | 2            |                                            |
| 4          | ……                 | ……         |                                            |
| M + 1      | Cell Voltage M       | 2            |                                            |
| M + 2      | Number of Monitored Temperatures N | 1            |                                            |
| M + 3      | Temperature 1        | 2            |                                            |
| M + 4      | Temperature 2        | 2            |                                            |
| M + 5      | ……                 | ……         |                                            |
| M + N + 2  | Temperature N        | 2            | A value of 0x8000 indicates no such temperature, and the corresponding parameter is hidden |
| M + N + 3  | PACK Current         | 2            | Positive for charging, negative for discharging, unit: 10mA, represented in two's complement |
| M + N + 4  | PACK Total Voltage   | 2            |                                            |
| M + N + 5  | PACK Remaining Capacity | 2            | Unit: 10mAH                                |
| M + N + 6  | Number of User-Defined Items P = 9 | 1            |                                            |
| M + N + 7  | PACK Full Charge Capacity | 2            | Unit: 10mAH                                |
| M + N + 8  | Charge-Discharge Cycle Count | 2            |                                            |
| M + N + 9  | PACK Design Capacity | 2            | Unit: 10mAH                                |
| M + N + 10 | Pack Soc            | 1            | Unit: 1%                                   |
| M + N + 11 | Cumulative Charge Capacity | 4            | Unit: 1AH                                  |
| M + N + 12 | Cumulative Discharge Capacity | 4            | Unit: 1AH                                  |
| M + N + 13 | Pack Soh            | 1            | Unit: 1%                                   |
| M + N + 14 | Independent Total Voltage 1 | 2            | Unit: mV                                   |
| M + N + 15 | Independent Current 1 | 2            | Unit: 10mA                                 |
| M + N + 16 | Summary Remaining Capacity | 4            | Unit: 10mAH                                |
| M + N + 17 | Summary Full Charge Capacity | 4            | Unit: 10mAH                                |

### 4.2. Get PACK Alarm Data (44H)

#### Table A.13 Get PACK Alarm Data Command Information

| Sequence | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 44H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is 1 Byte, i.e., COMMAND:

- COMMAND = FFH, get all PACK alarm data.
- COMMAND = 01H, get PACK1 alarm data.
- ……
- COMMAND = 0FH, get PACK15 alarm data.

Note: Applicable to RS232 interface with BMS address set to 1. Combined with RS485 using a master-slave structure, multiple PACK data can be obtained. If the BMS address is not equal to 1 or RS485 is not in a master-slave structure, only the alarm data of this PACK can be obtained, and COMMAND can be set to 01H or FFH.

#### Table A.14 Get PACK Alarm Data Response Information

| Sequence | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: DATA_INFO consists of INFOFLAG and WARNSTATE. WARNSTATE details are shown in Table A.15.
INFOFLAG is 00H or 01H.

#### Table A.15 Analog DATA_INFO Data Transmission Sequence

| Sequence | Content                       | DATAI Byte Count | Remarks     |
| ----- | -------------------------- | ------------ | --------- |
| 1     | * PACK Quantity M / COMMAND Value | 1            |           |
| 2     | PACK 1 Alarm Data Info          |              | See Table A.16 |
| 3     | ……                       | ……         |           |
| M + 1 | PACK M Alarm Data Info          |              | See Table A.16 |

* When COMMAND in the command is FFH, the response information is the PACK quantity; for other values, the response information is the numerical value of COMMAND.

#### Table A.16 Single Battery Group Alarm Data Content and Transmission Sequence

| Sequence       | Content                | DATAI Byte Count | Remarks            |
| ---------- | ------------------- | ------------ | --------------- |
| 1          | Number of Battery Cells M      | 1            |                 |
| 2          | Battery Cell Voltage 1 Alarm | 1            |                 |
| 3          | Battery Cell Voltage 2 Alarm | 1            |                 |
| 4          | ……                | ……         |                 |
| M + 1      | Battery Cell Voltage M Alarm | 1            |                 |
| M + 2      | Number of Monitored Temperatures N      | 1            |                 |
| M + 3      | Temperature 1 Alarm         | 1            |                 |
| M + 4      | Temperature 2 Alarm         | 1            |                 |
| M + 5      | ……                | ……         |                 |
| M + N + 2  | Temperature N Alarm         | 1            |                 |
| M + N + 3  | PACK Charge Current Alarm   | 1            |                 |
| M + N + 4  | PACK Total Voltage Alarm     | 1            |                 |
| M + N + 5  | PACK Discharge Current Alarm   | 1            |                 |
| M + N + 6  | Protection Status 1          | 1            | See Table A.17     |
| M + N + 7  | Protection Status 2          | 1            | See Table A.18     |
| M + N + 8  | Indication Status            | 1            | See Table A.19     |
| M + N + 9  | Control Status            | 1            | See Table A.20     |
| M + N + 10 | Fault Status 1          | 1            | See Table A.21     |
| M + N + 11 | Balancing Status 1          | 1            | Balancing status for cells 1-8  |
| M + N + 12 | Balancing Status 2          | 1            | Balancing status for cells 9-16 |
| M + N + 13 | Alarm Status 1          | 1            | See Table A.24     |
| M + N + 14 | Alarm Status 2          | 1            | See Table A.25     |
| M + N + 15 | Authentication Fault 1          | 1            | See Table A.26     |
| M + N + 16 | Indication Status 2          | 1            | See Table A.27     |
| M + N + 17 | Active Balancing Status 1      | 1            | Active balancing status for cells 1-8  |
| M + N + 18 | Active Balancing Status 2      | 1            | Active balancing status for cells 9-16 |
| M + N + 19 | Fault Status 3          | 1            | See Table A.28     |

Alarm Byte Description:

- 00H: Normal;
- 01H: Below lower limit;
- 02H: Above upper limit;
- 80H～EFH: User-defined;
- F0H: Other faults.

#### Table A.17 Protection Status 1 Explanation

| BIT | Content         | Remarks                    |
| --- | ------------ | ----------------------- |
| 7   | Charger High Voltage   | 1: Charger high voltage protection 0: None |
| 6   | Short Circuit         | 1: Short circuit protection 0: None       |
| 5   | Discharge Overcurrent Protection | 1: Discharge overcurrent protection 0: None   |
| 4   | Charge Overcurrent Protection | 1: Charge overcurrent protection 0: None   |
| 3   | Total Voltage Overdischarge Protection | 1: Total voltage overdischarge protection 0: None   |
| 2   | Total Voltage Overvoltage Protection | 1: Total voltage overvoltage protection 0: None   |
| 1   | Single Cell Under-voltage Protection | 1: Single Cell Under-voltage Protection 0: None   |
| 0   | Single Cell Over-voltage Protection | 1: Single Cell Over-voltage Protection 0: None   |

#### Table A.18 Protection Status 2 Explanation

| BIT | Content                 | Remarks                   |
| --- | -------------------- | ---------------------- |
| 7   | Fully                   | 1: Fully 0: None |
| 6   | Ambient Low Temperature Protection | 1: Ambient Low Temperature Protection 0: None  |
| 5   | Ambient High Temperature Protection | 1: Ambient High Temperature Protection 0: None  |
| 4   | MOS High Temperature Protection | 1: MOS High Temperature Protection 0: None   |
| 3   | Discharge Low Temperature Protection (Cell) | 1: Discharge Low Temperature Protection 0: None  |
| 2   | Charge Low Temperature Protection (Cell) | 1: Charge Low Temperature Protection 0: None  |
| 1   | Discharge High Temperature Protection (Cell) | 1: Discharge High Temperature Protection 0: None  |
| 0   | Charge High Temperature Protection (Cell) | 1: Charge High Temperature Protection 0: None  |

#### Table A.19 Indication Status 3 Explanation

| BIT | Content             | Remarks                  |
| --- | ---------------- | --------------------- |
| 7   | Heating Film Indicator       | 1: ON 0: OFF          |
| 6   | Shutdown             | 1: Shutdown 0: None         |
| 5   | ACin             | 1: Present 0: None           |
| 4   | Charger Reverse Connection Indicator   | 1: Reverse Connection 0: None         |
| 3   | Pack Power Supply Indicator | 1: Pack Power Supply 0: Not Used |
| 2   | DFET Indicator         | 1: ON 0: OFF          |
| 1   | * CFET Indicator       | 1: ON 0: OFF          |
| 0   | Current Limiting Indicator         | 1: ON 0: OFF          |

* If either the charging MOS or the current limiting circuit is ON, it is displayed as ON; if both are OFF, it is displayed as OFF.

#### Table A.20 Control Status 4 Explanation

| BIT | Content           | Remarks                |
| --- | -------------- | ------------------- |
| 7   | Test Mode       | 1: Enable 0: Disable     |
| 6   | System Lock Function     | 1: Enable 0: Disable     |
| 5   | LED Alarm Function    | 1: Disable 0: Enable     |
| 4   | Charge Current Limiting Function   | 1: Disable 0: Enable     |
| 3   | Current Limiting Gear       | 1: Low Gear 0: High Gear |
| 2   | DFET Function       | 1: Enable 0: Disable     |
| 1   | CFET Function       | 1: Enable 0: Disable     |
| 0   | Buzzer Alarm Function | 1: Enable 0: Disable     |

#### Table A.21 Fault Status 5 Explanation

| BIT | Content                  | Remarks            |
| --- | --------------------- | --------------- |
| 7   | Heating Film Fault            | 1: Fault 0: Normal |
| 6   | Current Limiting Fault              | 1: Fault 0: Normal |
| 5   | Sampling Chip Fault          | 1: Fault 0: Normal |
| 4   | Cell Fault              | 1: Fault 0: Normal |
| 3   | Communication Fault              | 1: Fault 0: Normal |
| 2   | Temperature Sensor Fault (NTC) | 1: Fault 0: Normal |
| 1   | Discharge MOS Fault           | 1: Fault 0: Normal |
| 0   | Charge MOS Fault           | 1: Fault 0: Normal |

#### Table A.22 Control Status 6 Explanation

| BIT | Content       | Remarks            |
| --- | ---------- | --------------- |
| 7   | Cell Low Temperature   | 1: Disable 0: Enable |
| 6   | Cell High Temperature   | 1: Disable 0: Enable |
| 5   | Discharge Overcurrent   | 1: Disable 0: Enable |
| 4   | Charge Overcurrent   | 1: Disable 0: Enable |
| 3   | Total Voltage Under-discharge | 1: Disable 0: Enable |
| 2   | Total Voltage Overcharge | 1: Disable 0: Enable |
| 1   | Single Cell Under-discharge   | 1: Disable 0: Enable |
| 0   | Single Cell Overcharge   | 1: Disable 0: Enable |

#### Table A.23 Control Status 7 Explanation

| BIT | Content     | Remarks            |
| --- | -------- | --------------- |
| 7   | Reserved     |                 |
| 6   | Reserved     |                 |
| 5   | Reserved     |                 |
| 4   | Reserved     |                 |
| 3   | Reserved     |                 |
| 2   | Reserved     |                 |
| 1   | Ambient Temperature | 1: Disable 0: Enable |
| 0   | MOS High Temperature  | 1: Disable 0: Enable |

#### Table A.24 Alarm Status 1 Explanation

| BIT | Content         | Remarks            |
| --- | ------------ | --------------- |
| 7   | Reserved         |                 |
| 6   | Reserved         |                 |
| 5   | Discharge Overcurrent Alarm | 1: Alarm 0: Normal |
| 4   | Charge Overcurrent Alarm | 1: Alarm 0: Normal |
| 3   | Total Voltage Low Alarm | 1: Alarm 0: Normal |
| 2   | Total Voltage Overvoltage Alarm | 1: Alarm 0: Normal |
| 1   | Single Cell Low Voltage Alarm | 1: Alarm 0: Normal |
| 0   | Single Cell Overvoltage Alarm | 1: Alarm 0: Normal |

#### Table A.25 Alarm Status 2 Explanation

| BIT | Content                 | Remarks            |
| --- | -------------------- | --------------- |
| 7   | Low Battery Alarm           | 1: Alarm 0: Normal |
| 6   | MOS High Temperature Alarm          | 1: Alarm 0: Normal |
| 5   | Ambient Low Temperature Alarm         | 1: Alarm 0: Normal |
| 4   | Ambient High Temperature Alarm         | 1: Alarm 0: Normal |
| 3   | Discharge Low Temperature Alarm (Cell) | 1: Alarm 0: Normal |
| 2   | Charge Low Temperature Alarm (Cell) | 1: Alarm 0: Normal |
| 1   | Discharge High Temperature Alarm (Cell) | 1: Alarm 0: Normal |
| 0   | Charge High Temperature Alarm (Cell) | 1: Alarm 0: Normal |

#### Table A.26 Fault Status 8 Explanation

| BIT | Content              | Remarks            |
| --- | ----------------- | --------------- |
| 7   | MCU Overvoltage           | 1: Fault 0: Normal |
| 6   | Battery Pack Lock        | 1: Fault 0: Normal |
| 5   | Master/Slave Offline Status | 1: Fault 0: Normal |
| 4   | Trip Unit Fault        | 1: Fault 0: Normal |
| 3   | Trip Unit Status        | 1: Fault 0: Normal |
| 2   | Current Sensing Resistor Fault      | 1: Fault 0: Normal |
| 1   | Temperature Difference Fault          | 1: Fault 0: Normal |
| 0   | Total Voltage Fault          | 1: Fault 0: Normal |

#### Table A.27 Indication Status 9 Explanation

| BIT | Content                     | Remarks              |
| --- | ------------------------ | ----------------- |
| 7   | Reserved                     | 1:  0:           |
| 6   | Reserved                     | 1:  0:           |
| 5   | Reserved                     | 1:  0:           |
| 4   | Reserved                     | 1:  0:           |
| 3   | Reserved                     | 1:  0:           |
| 2   | Current Limiting Off (Hardware Overvoltage Protection) | 1: Protected 0: Not Protected |
| 1   | WiFi Background Connection             | 1: Connected 0: Not Connected |
| 0   | Bluetooth Connection                 | 1: Connected 0: Not Connected |

#### Table A.28 Fault Status 10 Explanation

| BIT | Content    | Remarks            |
| --- | ------- | --------------- |
| 7   | Reserved    | 1: Fault 0: Normal |
| 6   | Reserved    | 1: Fault 0: Normal |
| 5   | Reserved    | 1: Fault 0: Normal |
| 4   | Reserved    | 1: Fault 0: Normal |
| 3   | Reserved    | 1: Fault 0: Normal |
| 2   | Reserved    | 1: Fault 0: Normal |
| 1   | Reserved    | 1: Fault 0: Normal |
| 0   | 12V Fault | 1: Fault 0: Normal |

### 4.3. Host PC Test Tool Write MCU Information (7EH)

#### Table A.29 Host PC Write MCU Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 7EH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 07H + NH.

COMMAND_INFO format is as follows:

| Device | Address                                                    | Length | Data |
| ---- | ------------------------------------------------------- | ---- | ---- |
| Byte | 1                                                       | 4    | 2    |
|      | 00: MCU FLASH<br />01: External FLASH <br />02: External EEPROM |      |      |

#### Table A.30 Host PC Write MCU Information Response

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.4. Host PC Test Tool Read MCU Information (7FH)

#### Table A.31 Host PC Read MCU Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 7FH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 07H.

COMMAND_INFO format is as follows:

| Device | Address                                                    | Length |
| ---- | ------------------------------------------------------- | ---- |
| Byte | 1                                                       | 4    |
|      | 00: MCU FLASH<br />01: External FLASH <br />02: External EEPROM |      |

#### Table A.32 Host PC Read MCU Information Response

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | COMMAND_INFO | CHKSUM | EOI |

COMMAND_INFO format is as follows:

| Device | Address                                                    | Length | Data |
| ---- | ------------------------------------------------------- | ---- | ---- |
| Byte | 1                                                       | 4    | 2    |
|      | 00: MCU FLASH<br />01: External FLASH <br />02: External EEPROM |      |      |

Note: LENID = 07H + N

### 4.5. Read Inverter Protocol List Number (60H)

#### Table A.33 Read Inverter Protocol List Number Command Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 60H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.34 Read Inverter Protocol List Number Response Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = NH.

DATA_INFO is variable length Byte, format is:

| CAN Protocol Count | Protocol Number | Protocol Number | 485 Protocol Count | Protocol Number | Protocol Number |
| ------------ | -------- | -------- | ------------ | -------- | -------- |
| Byte         | 1        | 1        | 1            | ……     | 1        |

### 4.6. Read Inverter Protocol List Name (61H)

#### Table A.35 Read Inverter Protocol List Name Command Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 61H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = NH.

DATA_INFO is N Byte, format is

| Language Type | Protocol Type               | Protocol Count             | Protocol Number | Protocol Number |
| -------- | ---------------------- | -------------------- | -------- | -------- |
| Byte     | 1                      | 1                    | 1        | 1        |
|          | 00: English<br />01: Chinese | 00: CAN<br />01: 485 |          |          |

#### Table A.36 Read Inverter Protocol List Name Response Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 04H.

| Name Count | Protocol Number | Name | Protocol Number | Name |
| -------- | -------- | ---- | -------- | ---- |
| Byte     | 1        | 1    | n        | 1    |

Explanation: n: Name string length, string ends with null: '\0'

---

### 4.7. Read Current Inverter Protocol (62H)

#### Table A.37 Read Inverter Protocol Command Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 62H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.38 Read Inverter Protocol Response Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 04H.

DATA_INFO is 2 Bytes, where the first byte is the CAN protocol number and the second byte is the 485 protocol number.

### 4.8. Set Current Inverter Protocol (63H)

#### Table A.39 Set Inverter Protocol Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | 63H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 04H.

COMMAND_INFO is 2 Bytes, where the first byte is the CAN protocol number, the second byte is the 485 protocol number, and number 0xFF indicates disabling this type of protocol (use 0xFF with caution).

#### Table A.40 Set Inverter Protocol Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 04H.

### 4.9. Get PACK Quantity (90H)

#### Table A.41 Get PACK Quantity Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | 90H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

When the BMS address setting is not equal to 1, the PACK quantity response is fixed at 1. When the BMS address setting is 1, combined with the RS485 master-slave mode, the PACK quantity is determined based on the actual number of battery packs.

#### Table A.42 Get PACK Quantity Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 02H.

DATA_INFO is 1 Byte, which is the PACK quantity. The maximum PACK quantity is 32.

### 4.10. Control Command (99H)

#### Table A.43 Control Command Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | 99H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is 1 Byte, which is the control command:

- COMMAND_INFO = 02H, Enable static balancing.
- COMMAND_INFO = 03H, Disable static balancing.
- COMMAND_INFO = 04H, Disable system lock.
- COMMAND_INFO = 05H, Enable system lock.
- COMMAND_INFO = 06H, Enable LED alarm function.
- COMMAND_INFO = 07H, Disable LED alarm function.
- COMMAND_INFO = 08H, Select high current limit gear.
- COMMAND_INFO = 09H, Select low current limit gear.
- COMMAND_INFO = 0AH, Enable current limiting function.
- COMMAND_INFO = 0BH, Disable current limiting function.
- COMMAND_INFO = 0CH, Disable buzzer alarm function.
- COMMAND_INFO = 0DH, Enable buzzer alarm function.
- COMMAND_INFO = 0EH, CAN communication protocol selection - PACE.
- COMMAND_INFO = 0FH, CAN communication protocol selection - PYLON.
- COMMAND_INFO = 10H, CAN communication protocol selection - GROWATT.
- COMMAND_INFO = 11H, CAN communication protocol selection - HOZONIE.
- COMMAND_INFO = 12H, CAN communication protocol selection - SOFAR.
- COMMAND_INFO = D0H~DFH, User-defined commands.

If a certain function is not available, the operation will prompt failure.

#### Table A.44 Control Command Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.11. Charge MOSFET Control (9AH)

#### Table A.45 Charge MOSFET Control Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | 9AH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is 1 Byte, which is the charge MOS control:

- COMMAND_INFO = 00H, Enable charge MOSFET.
- COMMAND_INFO = 01H, Disable charge MOSFET.

Note: If the discharge MOSFET is in a forced off state or is discharging, the charge MOSFET cannot be disabled.

#### Table A.46 Charge MOSFET Control Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 02H.

DATA_INFO data is 1 Byte, which is the status3 indicator status, detailed in Table A.19.

### 4.12. Discharge MOSFET Control (9BH)

#### Table A.47 Discharge MOSFET Control Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | 9BH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is 1 Byte, which is the discharge MOS control:

- COMMAND_INFO = 00H, Enable discharge MOSFET.
- COMMAND_INFO = 01H, Disable discharge MOSFET.

Note: If the charge MOSFET is in a forced off state or is charging, the discharge MOSFET cannot be disabled.

#### Table A.48 Discharge MOSFET Control Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format     | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 02H.

DATA_INFO data is 1 Byte, indicating the status3 indicator status. For details, refer to Table A.19.

### 4.13. Shutdown/Hibernate (9CH)

#### Table A.49 Shutdown/Hibernate Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | 9CH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.50 Shutdown/Hibernate Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H. Start the timer to enter hibernate state.

### 4.14. Read Cell Hibernate Parameters (A0H)

#### Table A.51 Read Cell Hibernate Parameters Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | A0H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.52 Read Cell Hibernate Parameters Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 08H.

DATA_INFO is 4 Bytes, representing the hibernate cell voltage and hibernate delay time. For details, see the table below.

#### Table A.53 Hibernate Parameters DATA_INFO Content and Transmission Order

| Sequence | Content               | DATA Byte Count | Remarks |
| ---- | ------------ | ------------ | ---- |
| 1        | Hibernate Cell Voltage | 2               |         |
| 2        | Hibernate Delay Time   | 2               |         |

### 4.15. Read History Records (A1H)

#### Table A.54 Read History Records Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | A1H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 04H,

COMMAND_INFO is 2 Bytes, representing the nth record.

#### Table A.55 Read History Records Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 90H,

DATA_INFO is 72 Bytes, representing the content of the nth record. For details, see the table below.

#### Table A.56 History Record Information Content and Transmission Order

| Sequence | Content                      | DATA Byte Count | Remarks                   |
| ---- | --------------- | ------------ | ------------------ |
| 1        | Record Generation Time-Year  | 1               |                           |
| 2        | Record Generation Time-Month | 1               |                           |
| 3        | Record Generation Time-Day   | 1               |                           |
| 4        | Record Generation Time-Hour  | 1               |                           |
| 5        | Record Generation Time-Minute| 1               |                           |
| 6        | Record Generation Time-Second| 1               |                           |
| 7        | Number of Strings            | 1               |                           |
| 8        | First String Voltage         | 2               |                           |
| ...  | ...             |              |                    |
|          | nth String Voltage           | 2               |                           |
|          | Number of Temperatures       | 1               |                           |
|          | Temperature 1                | 2               |                           |
| ...  | ...             |              |                    |
|          | Temperature m                | 2               |                           |
|          | Current                      | 2               |                           |
|          | Total Voltage                | 2               |                           |
|          | Remaining Capacity           | 2               |                           |
|          | Full Charge Capacity         | 2               |                           |
|          | Protection Status 1          | 1               |                           |
|          | Protection Status 2          | 1               |                           |
|          | Fault Status 5               | 1               |                           |
|          | Alarm Status 1               | 1               |                           |
|          | Alarm Status 2               | 1               |                           |
|          | Indicator Status 3           | 1               |                           |
|          | Cycle Count                  | 2               |                           |
|          | Fault Status 8               | 1               |                           |
|          | Fault Status 10              | 1               |                           |
|          | Status Record                | 2               | Details in Status Record Explanation Table |

#### Table A.57 Status Record Explanation

| BIT  | Content    | Remarks                         |
| ---- | ---- | ------------------ |
| 0    | Power On   | Recorded once when device powers on |
| 1    | Reserved   |                                 |
| 2    | Reserved   |                                 |
| 3    | Reserved   |                                 |
| 4    | Reserved   |                                 |
| 5    | Reserved   |                                 |
| 6    | Reserved   |                                 |
| 7~15 | Reserved   |                                 |

### 4.16. Restore Default Parameters (A4H)

#### Table A.58 Restore Default Parameters Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | A4H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.59 Restore Default Parameters Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.17. Set Capacity Release Percentage Parameters (A5H)

#### Table A.60 Set Capacity Release Percentage Parameters Command Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | A5H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is 1 Byte, which is the charging cutoff SOC (74-97).

#### Table A.61 Set Capacity Release Percentage Parameter Response Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.18. Get PACK Capacity Information (A6H)

#### Table A.62 Get PACK Capacity Information Command Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | A6H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.63 Get PACK Capacity Information Response Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 0CH.

DATA_INFO is 6 Byte, which is the PACK capacity information, detailed in the table below.

#### Table A.64 Get PACK Capacity Information Content and Transmission Order

| Sequence | Content        | DATAI Byte Count | Remarks       |
| ---- | -------- | ------------ | ----------- |
| 1        | Remaining Capacity | 2            | Unit: 10mAH |
| 2        | Full Charge Capacity | 2         | Unit: 10mAH |
| 3        | Design Capacity | 2            | Unit: 10mAH |

### 4.19. Set PACK Capacity Information (A7H)

#### Table A.65 Set PACK Capacity Information Command Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | A7H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 0CH.

COMMAND_INFO is 6 Byte, which is the PACK capacity information, detailed in the table below.

#### Table A.66 Set PACK Capacity Information Content and Transmission Order

| Sequence | Content        | DATAI Byte Count | Remarks       |
| ---- | -------- | ------------ | ----------- |
| 1        | Remaining Capacity | 2            | Unit: 10mAH |
| 2        | Full Charge Capacity | 2         | Unit: 10mAH |
| 3        | Design Capacity | 2            | Unit: 10mAH |

#### Table A.67 Set PACK Capacity Information Response Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.20. Set Cell Sleep Parameters (A8H)

#### Table A.68 Set Cell Sleep Parameters Command Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | A8H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 08H.

COMMAND_INFO is 4 Byte, which is the PACK capacity information, detailed in the table below.

#### Table A.69 Cell Sleep Parameter Information Content and Transmission Order

| Sequence | Content              | DATAI Byte Count | Remarks |
| ---- | ------------ | ------------ | ---- |
| 1        | Cell Sleep Voltage  | 2                |         |
| 2        | Sleep Delay Time    | 2                |         |

#### Table A.70 Set Cell Sleep Parameters Response Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.21. Calibrate Reference Voltage (A9H)

#### Table A.71 Calibrate Reference Voltage Command Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | A9H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 04H.

COMMAND_INFO is 2 Byte, which is the MCU reference voltage.

#### Table A.72 Calibrate Reference Voltage Response Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.22. Current Zero-Point Calibration (AAH)

#### Table A.73 Current Zero-Point Calibration Command Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count      | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format          | SOI | VER | ADR | 46H | AAH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 04H.

COMMAND_INFO is 2 Byte. The unique zero-point calibration command is COMMAND_INFO = 4321;

#### Table A.74 Current Zero-Point Calibration Response Information

| Sequence Number | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format     | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.23. Calibrate Discharge Current (ABH)

#### Table A.75 Calibrate Discharge Current Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | ABH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 04H.

COMMAND_INFO is 2 Byte.

- COMMAND_INFO = 0, Reset;
- COMMAND_INFO = (50, 600), Low-range current calibration value.

#### Table A.76 Calibrate Discharge Current Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.24. Calibrate Charge Current (ACH)

#### Table A.77 Calibrate Charge Current Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | ACH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 04H.

COMMAND_INFO is 2 Byte.

- COMMAND_INFO = 0, Reset;
- COMMAND_INFO = (50, 15000), Low-range current calibration value.

#### Table A.78 Calibrate Charge Current Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.25. Calibrate Total Voltage (ADH)

#### Table A.79 Calibrate Total Voltage Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | ADH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 04H.

COMMAND_INFO is 2 Byte, which is the set total voltage.

#### Table A.80 Calibrate Total Voltage Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.26. Set Full Charge Parameters and Capacity Warning (AEH)

#### Table A.81 Set Full Charge Parameters and Capacity Warning Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | AEH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 08H or 0AH.

COMMAND_INFO is 4 or 5 Byte, which are the full charge cutoff parameters and low capacity warning value. See details in the table below.

#### Table A.82 Full Charge Parameters and Capacity Warning Information Content and Transmission Order

| Sequence | Content             | DATAI Byte Count | Remarks                 |
| ---- | ------------ | ------------ | ---------------------- |
| 1        | Full Charge Cutoff Voltage | 2            | Unit: mV               |
| 2        | Full Charge Cutoff Current | 2            | Unit: mA               |
| 3        | Low Capacity Warning Value | 1            | Unit: % (LENID = 0AH) |

#### Table A.83 Set Full Charge Parameters and Capacity Warning Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

---

### 4.27. Read Full Charge Parameters and Capacity Warning (AFH)

#### Table A.84 Read Full Charge Parameters and Capacity Warning Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | AFH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.85 Read Full Charge Parameters and Capacity Warning Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

If LENID = 0AH.

DATA_INFO is 5 Byte, which are the full charge cutoff parameters and low capacity warning value. See details in the table below.

#### Table A.86 Full Charge Parameters and Capacity Warning Information Content and Transmission Order

| Sequence | Content             | DATAI Byte Count | Remarks     |
| ---- | ------------ | ------------ | -------- |
| 1        | Full Charge Cutoff Voltage | 2            | Unit: mV |
| 2        | Full Charge Cutoff Current | 2            | Unit: mA |
| 3        | Low Capacity Warning Value | 1            | Unit: %  |

### 4.28. Get BMS Time and Date (B1H)

#### Table A.87 Get BMS Time and Date Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | B1H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.88 Get BMS Time and Date Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 0CH.

DATA_INFO is 6 Bytes, representing the time and date information. Details are shown in the following table.

#### Table A.89 BMS Time and Date Information Content and Transmission Order

| Sequence No. | Content | DATAI Byte Count | Remarks                  |
| ---- | ---- | ------------ | --------------------- |
| 1            | Year    | 1                | Actual Value = Transmitted Value + 2000 |
| 2            | Month   | 1                |                                           |
| 3            | Day     | 1                |                                           |
| 4            | Hour    | 1                |                                           |
| 5            | Minute  | 1                |                                           |
| 6            | Second  | 1                |                                           |

### 4.29. Set BMS Time and Date (B2H)

#### Table A.90 Set BMS Time and Date Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | B2H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 0CH,

COMMAND_INFO is 6 Bytes, representing the time and date information. Details are shown in the following table.

#### Table A.91 BMS Time and Date Information Content and Transmission Order

| Sequence No. | Content | DATAI Byte Count | Remarks                  |
| ---- | ---- | ------------ | --------------------- |
| 1            | Year    | 1                | Transmitted Value = Actual Value - 2000 |
| 2            | Month   | 1                |                                           |
| 3            | Day     | 1                |                                           |
| 4            | Hour    | 1                |                                           |
| 5            | Minute  | 1                |                                           |
| 6            | Second  | 1                |                                           |

#### Table A.92 Set BMS Time and Date Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.30. Clear History Records (B3H)

#### Table A.93 Clear History Records Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | B3H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.94 Clear History Records Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.31. Set Battery String Count (B4H)

#### Table A.95 Set Battery String Count Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | B4H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is 1 Byte, representing the battery string count [13-16] strings.

#### Table A.96 Set Battery String Count Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.32. Set Balancing Parameters (B5H)

#### Table A.97 Set Balancing Parameters Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | B5H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 08H.

COMMAND_INFO is 4 Bytes, representing the balancing start voltage and voltage difference. Details are shown in the following table.

#### Table A.98 Balancing Parameter Information Content and Transmission Order

| Sequence No. | Content              | DATAI Byte Count | Remarks     |
| ---- | ------------ | ------------ | -------- |
| 1            | Balancing Start Voltage | 2                | Unit: mV    |
| 2            | Balancing Start Voltage Difference | 2                | Unit: mV    |

#### Table A.99 Set Balancing Parameters Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.33. Read Balancing Parameters (B6H)

#### Table A.100 Read Balancing Parameters Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | B6H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.101 Read Balancing Parameters Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 08H.

DATA_INFO is 4 Bytes, specifically the balancing enable voltage and voltage difference. For details, refer to the table below.

#### Table A.102 Balancing Parameter Information Content and Transmission Order

| Sequence | Content         | DATAI Bytes | Remarks     |
| ---- | ------------ | ------------ | -------- |
| 1    | Balancing Enable Voltage | 2            | Unit: mV |
| 2    | Balancing Enable Voltage Difference | 2            | Unit: mV |

### 4.34. Set Timed Storage Interval (B7H)

#### Table A.103 Set Timed Storage Interval Command Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | B7H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is 1 Byte, representing the timed interval (0,120).

#### Table A.104 Set Timed Storage Interval Response Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

If LENID = 00H.

### 4.35. Read Timed Storage Interval (B8H)

#### Table A.105 Read Timed Storage Interval Command Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | B8H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.106 Read Timed Storage Interval Response Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

If LENID = 02H.

DATA_INFO is 1 Byte, representing the timed interval.

### 4.36. Set Timed Storage Start Time (B9H)

#### Table A.107 Set Timed Storage Start Time Command Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | B9H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 0CH.

COMMAND_INFO is 6 Bytes, representing the storage start time.

#### Table A.108 Set Timed Storage Start Time Response Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

If LENID = 00H.

### 4.37. Read Timed Storage Start Time (BAH)

#### Table A.109 Read Timed Storage Start Time Command Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | BAH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

If LENID = 00H.

#### Table A.110 Read Timed Storage Start Time Response Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 0CH.

DATA_INFO is 6 Bytes, representing the storage start time.

### 4.38. Set Timed Storage End Time (BBH)

#### Table A.111 Set Timed Storage End Time Command Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | BBH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 0CH.

COMMAND_INFO is 6 Bytes, representing the timed storage end time.

#### Table A.112 Set Timed Storage End Time Response Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

If LENID = 00H.

### 4.39. Read Timed Storage End Time (BCH)

#### Table A.113 Read Timed Storage End Time Command Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | BCH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.114 Read Timed Storage End Time Response Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Bytes | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

If LENID = 0CH.

DATA_INFO is 6 Bytes, representing the timed storage end time.

### 4.40. Set Charge/Discharge Cycle Count (BDH)

#### Table A.115 Set Charge/Discharge Cycle Count Command Information

| Sequence   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format     | SOI | VER | ADR | 46H | BDH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 04H.

COMMAND_INFO is 2 Byte, representing the cycle count.

#### Table A.116 Set Charge-Discharge Cycle Count Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

If LENID = 00H.

### 4.41. Get Software Version Information (C1H)

#### Table A.117 Get Software Version Information Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | C1H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.118 Get Software Version Information Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 28H or 50H.

DATA_INFO is the software version information + Bluetooth device name. The software version information is 20 characters, padded with spaces if less than 20 characters. The Bluetooth device name is 20 characters, padded with spaces if less than 20 characters.

The Bluetooth device name is dedicated to the baseboard with Bluetooth functionality and is not uploaded by devices without a Bluetooth module. The Bluetooth device name is only displayed after the BMS successfully establishes communication with the Bluetooth module; otherwise, it is not uploaded.

### 4.42. Get Product Information (C2H)

#### Table A.119 Get Product Information Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | C2H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.120 Get Product Information Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 50H or 28H.

DATA_INFO is the product information, which includes BMS production information (20 characters) and PACK production information (20 characters).

If LENID = 28H, then there is no PACK production information.

### 4.43. Input BMS Product Information (C3H)

#### Table A.121 Input BMS Product Information Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | C3H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 28H.

COMMAND_INFO is 20 Byte, representing the BMS production information (20 characters).

#### Table A.122 Input BMS Product Information Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.44. Input PACK Product Information (C4H)

#### Table A.123 Input PACK Product Information Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | C4H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 28H.

COMMAND_INFO is 20 Byte, representing the PACK product information (20 characters).

#### Table A.124 Input PACK Product Information Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.45. Get Internal Version Information (C6H)

#### Table A.125 Get Internal Version Information Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | C6H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.126 Get Internal Version Information Response Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note:

DATA_INFO is the software version information + hardware version information. The hardware version occupies the last 10 bytes, and the remaining bytes are for the software version, with a maximum of 30 bytes for the software version.

#### Table A.127 Cell Overcharge Parameter Information Content and Transmission Order

| Sequence | Content          | DATAI Byte Count | Remarks   |
| ---- | ------------ | ------------ | -------- |
| 1        | Internal Software Version | Max 30 bytes | ASCII code |
| 2        | Hardware Version          | 10           | ASCII code |

### 4.46. Set Cell Overcharge Parameters (D0H)

#### Table A.128 Set Cell Overcharge Parameters Command Information

| Sequence No. | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format     | SOI | VER | ADR | 46H | D0H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 10H.

COMMAND_INFO is 8 Bytes, representing the single-cell overcharge parameters. See the table below for details.

#### Table A.129 Single-cell Overcharge Parameter Information Content and Transmission Order

| No. | Content                     | DATAI Byte Count | Remarks                        |
| ---- | ---------------- | ------------ | --------------- |
| 1    | Single-cell Overcharge Function Control | 1            | 0: Disable 1: Enable |
| 2    | Single-cell Overcharge Alarm | 2            | Unit: mV        |
| 3    | Single-cell Overcharge Protection | 2            | Unit: mV        |
| 4    | Single-cell Overcharge Recovery | 2            | Unit: mV        |
| 5    | Single-cell Overcharge Protection Delay | 1            | Unit: 100ms (Value × 100 = actual ms) |

#### Table A.130 Set Single-cell Overcharge Parameter Response Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.47. Read Single-cell Overcharge Parameters (D1H)

#### Table A.131 Read Single-cell Overcharge Parameter Command Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | D1H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.132 Read Single-cell Overcharge Parameter Response Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 10H.

DATA_INFO is 8 Bytes, representing the single-cell overcharge parameters. See the table below for details.

#### Table A.133 Single-cell Overcharge Parameter Information Content and Transmission Order

| No. | Content                     | DATAI Byte Count | Remarks                        |
| ---- | ---------------- | ------------ | --------------- |
| 1    | Single-cell Overcharge Function Control | 1            | 0: Disable 1: Enable |
| 2    | Single-cell Overcharge Alarm | 2            | Unit: mV        |
| 3    | Single-cell Overcharge Protection | 2            | Unit: mV        |
| 4    | Single-cell Overcharge Recovery | 2            | Unit: mV        |
| 5    | Single-cell Overcharge Protection Delay | 1            | Unit: 100ms (Value × 100 = actual ms) |

### 4.48. Set Single-cell Over-discharge Parameters (D2H)

#### Table A.134 Set Single-cell Over-discharge Parameter Command Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | D2H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 10H.

COMMAND_INFO is 8 Bytes, representing the single-cell over-discharge parameters. See the table below for details.

#### Table A.135 Single-cell Over-discharge Parameter Information Content and Transmission Order

| No. | Content                     | DATAI Byte Count | Remarks                        |
| ---- | ---------------- | ------------ | --------------- |
| 1    | Single-cell Over-discharge Function Control | 1            | 0: Disable 1: Enable |
| 2    | Single-cell Over-discharge Alarm | 2            | Unit: mV        |
| 3    | Single-cell Over-discharge Protection | 2            | Unit: mV        |
| 4    | Single-cell Over-discharge Recovery | 2            | Unit: mV        |
| 5    | Single-cell Over-discharge Protection Delay | 1            | Unit: 100ms (Value × 100 = actual ms) |

#### Table A.136 Set Single-cell Over-discharge Parameter Response Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.49. Read Single-cell Over-discharge Parameters (D3H)

#### Table A.137 Read Single-cell Over-discharge Parameter Command Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | D3H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.138 Read Single-cell Over-discharge Parameter Response Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 10H.

DATA_INFO is 8 Bytes, representing the single-cell over-discharge parameters. See the table below for details.

#### Table A.139 Single-cell Over-discharge Parameter Information Content and Transmission Order

| No. | Content                     | DATAI Byte Count | Remarks                        |
| ---- | ---------------- | ------------ | --------------- |
| 1    | Single-cell Over-discharge Function Control | 1            | 0: Disable 1: Enable |
| 2    | Single-cell Over-discharge Alarm | 2            | Unit: mV        |
| 3    | Single-cell Over-discharge Protection | 2            | Unit: mV        |
| 4    | Single-cell Over-discharge Recovery | 2            | Unit: mV        |
| 5    | Single-cell Over-discharge Protection Delay | 1            | Unit: 100ms (Value × 100 = actual ms) |

### 4.50. Set Total Overcharge Parameters (D4H)

#### Table A.140 Set Total Overcharge Parameter Command Information

| No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | D4H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 10H.

COMMAND_INFO is 8 Bytes, representing the total overcharge parameters. See the table below for details.

#### Table A.141 Total Overcharge Parameter Information Content and Transmission Order

| Sequence No. | Content                   | DATAI Byte Count | Remarks                              |
| ---- | ---------------- | ------------ | --------------- |
| 1            | Overall Overcharge Function Control | 1                | 0: Disable 1: Enable                 |
| 2            | Overall Overcharge Alarm  | 2                | Unit: mV                             |
| 3            | Overall Overcharge Protection | 2                | Unit: mV                             |
| 4            | Overall Overcharge Recovery | 2                | Unit: mV                             |
| 5            | Overall Overcharge Protection Delay | 1                | Unit: 100ms (Value×100=Actual ms)    |

#### Table A.142 Response Information for Setting Overall Overcharge Parameters

| Sequence No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count     | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format         | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.51. Read Overall Overcharge Parameters (D5H)

#### Table A.143 Command Information for Reading Overall Overcharge Parameters

| Sequence No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count     | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format         | SOI | VER | ADR | 46H | D5H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

#### Table A.144 Response Information for Reading Overall Overcharge Parameters

| Sequence No.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count     | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format         | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 10H.

DATA_INFO is 8 Byte, which is the overall overcharge parameters. See the table below for details.

#### Table A.145 Overall Overcharge Parameter Information Content and Transmission Order

| Sequence No. | Content                   | DATAI Byte Count | Remarks                              |
| ---- | ---------------- | ------------ | --------------- |
| 1            | Overall Overcharge Function Control | 1                | 0: Disable 1: Enable                 |
| 2            | Overall Overcharge Alarm  | 2                | Unit: mV                             |
| 3            | Overall Overcharge Protection | 2                | Unit: mV                             |
| 4            | Overall Overcharge Recovery | 2                | Unit: mV                             |
| 5            | Overall Overcharge Protection Delay | 1                | Unit: 100ms (Value×100=Actual ms)    |

---

### 4.52. Set Overall Over-discharge Parameters (D6H)

**Table A.146 Command Information for Setting Overall Over-discharge Parameters**

| Sequence No.             | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | D6H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 10H.
COMMAND_INFO is 8 Byte, which is the overall over-discharge parameters. See the table below for details.

**Table A.147 Overall Over-discharge Parameter Information Content and Transmission Order**

| Sequence No. | Content                   | DATA Byte Count | Remarks                        |
| :--- | :--------------- | :---------- | :------------ |
| 1            | Overall Over-discharge Function Control | 1               | 0: Disable 1: Enable           |
| 2            | Overall Over-discharge Alarm | 2               | Unit: mV                       |
| 3            | Overall Over-discharge Protection | 2               | Unit: mV                       |
| 4            | Overall Over-discharge Recovery | 2               | Unit: mV                       |
| 5            | Overall Over-discharge Protection Delay | 1               | Unit: 100ms (Value×100=Actual ms) |

**Table A.148 Response Information for Setting Overall Over-discharge Parameters**

| Sequence No.             | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

### 4.53. Read Overall Over-discharge Parameters (D7H)

**Table A.149 Command Information for Reading Overall Over-discharge Parameters**

| Sequence No.             | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | D7H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.150 Response Information for Reading Overall Over-discharge Parameters**

| Sequence No.             | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 10H.
DATA_INFO is 8 Byte, which is the overall over-discharge parameters. See the table below for details.

**Table A.151 Overall Over-discharge Parameter Information Content and Transmission Order**

| Sequence No. | Content                   | DATA Byte Count | Remarks                        |
| :--- | :--------------- | :---------- | :------------ |
| 1            | Overall Over-discharge Function Control | 1               | 0: Disable 1: Enable           |
| 2            | Overall Over-discharge Alarm | 2               | Unit: mV                       |
| 3            | Overall Over-discharge Protection | 2               | Unit: mV                       |
| 4            | Overall Over-discharge Recovery | 2               | Unit: mV                       |
| 5            | Overall Over-discharge Protection Delay | 1               | Unit: 100ms (Value×100=Actual ms) |

---

### 4.54. Set Charging Overcurrent Parameters (D8H)

**Table A.152 Command Information for Setting Charging Overcurrent Parameters**

| Sequence No.             | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | D8H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 10H.
COMMAND_INFO is 8 Byte, which is the charging overcurrent parameters. See the table below for details.

**Table A.153 Charging Overcurrent Parameter Information Content and Transmission Order**

| Sequence No. | Content                   | DATA Byte Count | Remarks                        |
| :--- | :--------------- | :---------- | :------------ |
| 1            | Charging Overcurrent Function Control | 1               | 0: Disable 1: Enable           |
| 2            | Charging Overcurrent Alarm | 2               | Unit: A                        |
| 3            | Charging Overcurrent Protection | 2               | Unit: A                        |
| 4            | Charging Overcurrent Recovery | 2               | Unit: A                        |
| 5 | Charge Overcurrent Protection Delay | 1 | Unit: 100ms (Value × 100 = Actual ms) |

**Table A.154 Set Charge Overcurrent Parameters Response Information**

| Sequence Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1 | 1 | 1 | 1 | 1 | 2 | LENID/2 | 2 | 1 |
| **Format** | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 00H

### 4.55. Read Charge Overcurrent Parameters (D9H)

**Table A.155 Read Charge Overcurrent Parameters Command Information**

| Sequence Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1 | 1 | 1 | 1 | 1 | 2 | LENID/2 | 2 | 1 |
| **Format** | SOI | VER | ADR | 46H | D9H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 00H

**Table A.156 Read Charge Overcurrent Parameters Response Information**

| Sequence Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1 | 1 | 1 | 1 | 1 | 2 | LENID/2 | 2 | 1 |
| **Format** | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 10H.
DATA_INFO is 6 Bytes, which is the cell over-discharge parameter. See the table below for details.

**Table A.157 Charge Overcurrent Parameter Information Content and Transmission Order**

| Sequence Number | Content | DATA Byte Count | Remarks |
| :--- | :--------------- | :---------- | :------------ |
| 1 | Charge Overcurrent Function Control | 1 | 0: Disable 1: Enable |
| 2 | Charge Overcurrent Alarm | 2 | Unit: A |
| 3 | Charge Overcurrent Protection | 2 | Unit: A |
| 4 | Charge Overcurrent Protection Delay | 1 | Unit: ms |

---

### 4.56. Set Discharge Overcurrent 1 Parameters (DAH)

**Table A.158 Set Discharge Overcurrent 1 Parameters Command Information**

| Sequence Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1 | 1 | 1 | 1 | 1 | 2 | LENID/2 | 2 | 1 |
| **Format** | SOI | VER | ADR | 46H | DAH | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 10H.
COMMAND_INFO is 8 Bytes, which is the cell over-discharge parameter. See the table below for details.

**Table A.159 Discharge Overcurrent 1 Parameter Information Content and Transmission Order**

| Sequence Number | Content | DATA Byte Count | Remarks |
| :--- | :--------------- | :---------- | :------------ |
| 1 | Discharge Overcurrent Function Control | 1 | 0: Disable 1: Enable |
| 2 | Discharge Overcurrent Alarm | 2 | Unit: A |
| 3 | Discharge Overcurrent Protection | 2 | Unit: A |
| 4 | Discharge Overcurrent Recovery | 2 | Unit: A |
| 5 | Discharge Overcurrent Protection Delay | 1 | Unit: ms |

**Table A.160 Set Discharge Overcurrent 1 Parameters Response Information**

| Sequence Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1 | 1 | 1 | 1 | 1 | 2 | LENID/2 | 2 | 1 |
| **Format** | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

### 4.57. Read Discharge Overcurrent 1 Parameters (DBH)

**Table A.161 Read Discharge Overcurrent 1 Parameters Command Information**

| Sequence Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1 | 1 | 1 | 1 | 1 | 2 | LENID/2 | 2 | 1 |
| **Format** | SOI | VER | ADR | 46H | DBH | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.162 Read Discharge Overcurrent 1 Parameters Response Information**

| Sequence Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1 | 1 | 1 | 1 | 1 | 2 | LENID/2 | 2 | 1 |
| **Format** | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 10H.
DATA_INFO is 8 Bytes, which is the cell over-discharge parameter. See the table below for details.

**Table A.163 Discharge Overcurrent 1 Parameter Information Content and Transmission Order**

| Sequence Number | Content | DATA Byte Count | Remarks |
| :--- | :--------------- | :---------- | :------------ |
| 1 | Discharge Overcurrent Function Control | 1 | 0: Disable 1: Enable |
| 2 | Discharge Overcurrent Alarm | 2 | Unit: A |
| 3 | Discharge Overcurrent Protection | 2 | Unit: A |
| 4 | Discharge Overcurrent Recovery | 2 | Unit: A |
| 5 | Discharge Overcurrent Protection Delay | 1 | Unit: ms |

---

### 4.58. Set Battery High Temperature Parameters (DCH)

**Table A.164 Set Battery High Temperature Parameters Command Information**

| Sequence Number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1 | 1 | 1 | 1 | 1 | 2 | LENID/2 | 2 | 1 |
| **Format** | SOI | VER | ADR | 46H | DCH | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 1AH.
COMMAND_INFO is 13 Bytes, which is the cell over-discharge parameter. See the table below for details.

**Table A.165 Battery High Temperature Parameter Information Content and Transmission Order**

| Sequence Number | Content | DATA Byte Count | Remarks |
| :--- | :--------------- | :---------- | :-------------- |
| 1 | Cell High Temperature Function Control | 1 | 0: Disable 1: Enable |
| 2 | Charge High Temperature Alarm | 2 | Unit: 0.1K, Conversion: °C = (Value/10) - 273 |
| 3 | Charge High Temperature Protection | 2 | Unit: 0.1K, Conversion: °C = (Value/10) - 273 |
| 4 | Charge High Temperature Protection Recovery | 2 | Unit: 0.1K, Conversion: °C = (Value/10) - 273 |
| 5 | Discharge High Temperature Alarm | 2 | Unit: 0.1K, Conversion: °C = (Value/10) - 273 |
| 6 | Discharge High Temperature Protection | 2 | Unit: 0.1K, Conversion: °C = (Value/10) - 273 |
| 7    | Discharge High Temperature Protection Recovery | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |

**Table A.166 Response Information for Setting Battery High Temperature Parameters**

| Serial Number       | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

### 4.59. Read Battery High Temperature Parameters (DDH)

**Table A.167 Command Information for Reading Battery High Temperature Parameters**

| Serial Number       | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | DDH | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.168 Response Information for Reading Battery High Temperature Parameters**

| Serial Number       | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 1AH.
DATA_INFO is 13 Byte, representing the single-cell over-discharge parameters. See the table below for details.

**Table A.169 Battery High Temperature Parameter Information Content and Transmission Order**

| No. | Content                         | DATA Byte Count | Remarks                     |
| :--- | :--------------- | :---------- | :------------ |
| 1   | Cell High Temperature Function Control | 1           | 0: Disable 1: Enable |
| 2   | Charging High Temperature Alarm       | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 3   | Charging High Temperature Protection  | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 4   | Charging High Temperature Protection Recovery | 2 | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 5   | Discharge High Temperature Alarm      | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 6   | Discharge High Temperature Protection | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 7   | Discharge High Temperature Protection Recovery | 2 | Unit: 0.1K, Conversion: °C=(Value/10)-273 |

---

### 4.60. Set Battery Low Temperature Parameters (DEH)

**Table A.170 Command Information for Setting Battery Low Temperature Parameters**

| Serial Number       | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | DEH | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 1AH.
COMMAND INFO is 13 Byte, representing the single-cell over-discharge parameters. See the table below for details.

**Table A.171 Battery Low Temperature Parameter Information Content and Transmission Order**

| No. | Content                         | DATA Byte Count | Remarks                      |
| :--- | :--------------- | :---------- | :-------------- |
| 1   | Cell Low Temperature Function Control | 1           | 0: Disable 1: Enable  |
| 2   | Charging Low Temperature Alarm       | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 3   | Charging Low Temperature Protection  | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 4   | Charging Low Temperature Protection Recovery | 2 | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 5   | Discharge Low Temperature Alarm      | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 6   | Discharge Low Temperature Protection | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 7   | Discharge Low Temperature Protection Recovery | 2 | Unit: 0.1K, Conversion: °C=(Value/10)-273 |

**Table A.172 Response Information for Setting Battery Low Temperature Parameters**

| Serial Number       | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

### 4.61. Read Battery Low Temperature Parameters (DFH)

**Table A.173 Command Information for Reading Battery Low Temperature Parameters**

| Serial Number       | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | DFH | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.174 Response Information for Reading Battery Low Temperature Parameters**

| Serial Number       | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 1AH.
DATA_INFO is 13 Byte, representing the single-cell over-discharge parameters. See the table below for details.

**Table A.175 Battery Low Temperature Parameter Information Content and Transmission Order**

| No. | Content                         | DATA Byte Count | Remarks                     |
| :--- | :--------------- | :---------- | :------------ |
| 1   | Cell Low Temperature Function Control | 1           | 0: Disable 1: Enable |
| 2   | Charging Low Temperature Alarm       | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 3   | Charging Low Temperature Protection  | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 4   | Charging Low Temperature Protection Recovery | 2 | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 5   | Discharge Low Temperature Alarm      | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 6   | Discharge Low Temperature Protection | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 7   | Discharge Low Temperature Protection Recovery | 2 | Unit: 0.1K, Conversion: °C=(Value/10)-273 |

---

### 4.62. Set MOSFET High Temperature Parameters (E0H)

**Table A.176 Command Information for Setting MOSFET High Temperature Parameters**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | E0H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID=0EH
COMMAND\_INFO is 7Byte, which is the MOS high-temperature parameters, details as shown in the table below.

**Table A.177 MOSFET High-Temperature Parameter Information Content and Transmission Order**

| Seq No. | Content             | DATA Byte Count | Remarks            |
| :--- | :--------------- | :---------- | :-------------- |
| 1    | Cell Low-Temperature Function Control | 1           | 0: Disable 1: Enable  |
| 2    | MOS High-Temperature Alarm     | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 3    | MOS High-Temperature Protection     | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 4    | MOS High-Temperature Protection Recovery | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |

**Table A.178 Set MOSFET High-Temperature Parameter Response Information**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 00H。

### 4.63. Read MOSFET High-Temperature Parameters (E1H)

**Table A.179 Read MOSFET High-Temperature Parameter Command Information**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | E1H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 00H。

**Table A.180 Read MOSFET High-Temperature Parameter Response Information**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID=0EH
DATA\_INFO is 7 Byte, which is the MOS high-temperature parameters, details as shown in the table below.

**Table A.181 MOSFET High-Temperature Parameter Information Content and Transmission Order**

| Seq No. | Content             | DATA Byte Count | Remarks          |
| :--- | :--------------- | :---------- | :------------ |
| 1    | MOS High-Temperature Function Control  | 1           | 0: Disable 1: Enable |
| 2    | MOS High-Temperature Alarm     | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 3    | MOS High-Temperature Protection     | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |
| 4    | MOS High-Temperature Protection Recovery | 2           | Unit: 0.1K, Conversion: °C=(Value/10)-273 |

---

### 4.64. Set Discharge Overcurrent 2 Parameters (E2H)

**Table A.182 Set Discharge Overcurrent 2 Parameter Command Information**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | E2H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 06H or 0CH. Details as shown in the table below.

**Table A.183 Discharge Overcurrent 2 Parameter Information Content and Transmission Order**

| Seq No. | Content               | DATA Byte Count | Remarks                      |
| :--- | :----------------- | :---------- | ------------------------- |
| 1    | Discharge Overcurrent Protection 2     | 2           | Unit: A                    |
| 2    | Discharge Overcurrent Protection Delay 2 | 1           | Unit: 25ms (Value × 25 = actual ms)  |
| 3    | Charge Overcurrent Protection 2     | 2           | Unit: A (LENID = 0CH)     |
| 4    | Charge Overcurrent Protection Delay 2 | 1           | Unit: 25ms (Value × 25 = actual ms)  |

**Table A.184 Set Discharge Overcurrent 2 Parameter Response Information**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 00H。

### 4.65. Read Discharge Overcurrent 2 Parameters (E3H)

**Table A.185 Read Discharge Overcurrent 2 Parameter Command Information**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | E3H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 00H。

**Table A.186 Read Discharge Overcurrent 2 Parameter Response Information**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 0CH
DATA\_INFO is 6 Byte, which is the charge/discharge overcurrent, details as shown in the table below.

**Table A.187 Discharge Overcurrent 2 Parameter Information Content and Transmission Order**

| Seq No. | Content               | DATA Byte Count | Remarks                      |
| :--- | :----------------- | :---------- | ------------------------- |
| 1    | Discharge Overcurrent Protection 2     | 2           | Unit: A                    |
| 2    | Discharge Overcurrent Protection Delay 2 | 1           | Unit: 25ms (Value × 25 = actual ms)  |
| 3    | Charge Overcurrent Protection 2     | 2           | Unit: A                    |
| 4    | Charge Overcurrent Protection Delay 2 | 1           | Unit: 25ms (Value × 25 = actual ms)  |

---

### 4.66. Set Short-Circuit Delay Parameters (E4H)

**Table A.188 Set Short-Circuit Delay Parameter Command Information**

| Sequence Number      | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | E4H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 02H.
COMMAND\_INFO is 1 Byte, which is the short-circuit delay.
Short-circuit delay unit: 25μs (value×25=actual μs).

**Table A.189 Set Short-Circuit Delay Parameter Response Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

### 4.67. Read Short-Circuit Delay Parameter (E5H)

**Table A.190 Read Short-Circuit Delay Parameter Command Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :----------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | E5H | LENGTH | COMMAND INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.191 Read Short-Circuit Delay Parameter Response Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :-------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA INFO | CHKSUM | EOI |

**Note:** LENID = 02H.
DATA\_INFO is 1 Byte, which is the short-circuit delay.
Short-circuit delay unit: 25μs (value×25=actual μs).

---

### 4.68. Set Ambient Temperature Parameter (E6H)

**Table A.192 Set Ambient Temperature Parameter Command Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | E6H | LENGTH | COMMAND\_INFO | CHKSUM | EOI |

**Note:** LENID = 1AH.
COMMAND\_INFO is 13 Byte, which is the ambient temperature parameter, see the table below for details.

**Table A.193 Ambient Temperature Parameter Information Content and Transmission Order**

| No. | Content             | DATA Byte Count | Remarks            |
| :--- | :--------------- | :---------- | :-------------- |
| 1    | Ambient Function Control     | 1           | 0: Disable 1: Enable |
| 2    | Ambient Low-Temperature Alarm     | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 3    | Ambient Low-Temperature Protection     | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 4    | Ambient Low-Temperature Protection Recovery | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 5    | Ambient High-Temperature Alarm     | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 6    | Ambient High-Temperature Protection     | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 7    | Ambient High-Temperature Protection Recovery | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |

**Table A.194 Set Ambient Temperature Parameter Response Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA\_INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

### 4.69. Read Ambient Temperature Parameter (E7H)

**Table A.195 Read Ambient Temperature Parameter Command Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | E7H | LENGTH | COMMAND\_INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.196 Read Ambient Temperature Parameter Response Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA\_INFO | CHKSUM | EOI |

**Note:** LENID = 1AH.
DATA\_INFO is 13 Byte, which is the ambient temperature parameter, see the table below for details.

**Table A.197 Ambient Temperature Parameter Information Content and Transmission Order**

| No. | Content             | DATA Byte Count | Remarks            |
| :--- | :--------------- | :---------- | :-------------- |
| 1    | Ambient Function Control     | 1           | 0: Disable 1: Enable |
| 2    | Ambient Low-Temperature Alarm     | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 3    | Ambient Low-Temperature Protection     | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 4    | Ambient Low-Temperature Protection Recovery | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 5    | Ambient High-Temperature Alarm     | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 6    | Ambient High-Temperature Protection     | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |
| 7    | Ambient High-Temperature Protection Recovery | 2           | Unit: 0.1K, Conversion: ℃=(value/10)-273 |

### 4.70. Get Current Limit Parameter (EDH)

**Table A.198 Get Current Limit Parameter Command Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | EDH | LENGTH | COMMAND\_INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.199 Get Current Limit Parameter Response Information**

| **Sequence No.** | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA\_INFO | CHKSUM | EOI |

**Note:** LENID = 04H。
DATA\_INFO is 2 Byte, which is the current limiting activation current value, unit: A。

### 4.71. Set Current Limiting Parameter(EEH)

**Table A.200 Set Current Limiting Parameter Command Information**

| **Sequence No.**             | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | EEH | LENGTH | COMMAND\_INFO | CHKSUM | EOI |

**Note:** LENID = 04H。
COMMAND\_INFO is 2 Byte, which is the current limiting activation current value, unit: A。

**Table A.201 Set Current Limiting Parameter Response Information**

| **Sequence No.**             | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA\_INFO | CHKSUM | EOI |

**Note:** LENID = 00H。

---

### 4.72. Read Inverter Protocol(EBH)

**Table A.202 Read Inverter Protocol Command Information**

| **Sequence No.**             | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | EBH | LENGTH | COMMAND\_INFO | CHKSUM | EOI |

**Note:** LENID = 00H。

**Table A.203 Read Inverter Protocol Response Information**

| **Sequence No.**             | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA\_INFO | CHKSUM | EOI |

**Note:** LENID = 6H。
DATA\_INFO is 3 Byte, which is CAN protocol, 485 protocol, type. Details are shown in the table below.

**Table A.204 Inverter Protocol Content and Transmission Sequence**

| **Sequence No.** | **Content**     | **DATA Byte Count** | **Remarks**       |
| :--- | :------- | :---------- | :--------- |
| 1    | CAN Protocol | 1           | See Table 1 below |
| 2    | 485 Protocol | 1           | See Table 1 below |
| 3    | Type     | 1           | See Table 1 below |

### 4.73. Set Inverter Protocol(ECH)

**Table A.205 Set Inverter Protocol Command Information**

| **Sequence No.**             | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | ECH | LENGTH | COMMAND\_INFO | CHKSUM | EOI |

**Note:** LENID = 6H。
COMMAND\_INFO is 3 Byte, which is CAN protocol, 485 protocol, type. Details are shown in the table below.
Sending 0xFF indicates no change to the current protocol/type. When set to automatic mode, COMMAND\_INFO is FF FF 00.

**Table A.206 Inverter Protocol Content and Transmission Sequence**

| **Sequence No.** | **Content**     | **DATA Byte Count** | **Remarks**       |
| :--- | :------- | :---------- | :--------- |
| 1    | CAN Protocol | 1           | See Table 1 below |
| 2    | 485 Protocol | 1           | See Table 1 below |
| 3    | Type     | 1           | See Table 1 below |

**Table A.207 Set Inverter Protocol Response Information**

| **Sequence No.**             | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA\_INFO | CHKSUM | EOI |

**Note:** LENID = 00H。

**Table 1: Inverter Protocol Code Table** 

| **CAN Protocol**                     | **485 Protocol**                        | **Type**    |
| :--------------------------- | :------------------------------ | :------ |
| 00H PACE\_CAN                | 00H PACE\_MODBUS\_485           | 00 Automatic |
| 01H PYLON\_CAN(Deye\_CAN)    | 01H PYLON\_485 (Deye\_485)     | 01 Manual |
| 02H GROWATT\_CAN (Growatt) | 02H GROWATT\_485 (Growatt)    |         |
| 03H VICTRON\_CAN (Victron)   | 03H VOLTRON\_485(SUNNY)        |         |
| 04H SE\_CAN (Schneider)        | 04H SE\_485 (Schneider)           |         |
| 05H LUXPOWERTEK\_CAN (Pengcheng) | 05H PHOCOS\_485                 |         |
| 06H SRD\_CAN (SORO)       | 06H LUXPOWER\_485 (Pengcheng)       |         |
| 07H SMA\_CAN                 | 07H SOLAR\_485                  |         |
| 08H GOODWE\_CAN              | 08H LITHIUM\_485                |         |
| 09H STUDER\_CAN              | 09H EP\_485                     |         |
| 0AH SOFAR\_CAN (Sofar)       | 0AH RTU04\_485                  |         |
| 0BH PV\_CAN (Maysun)        | 0BH LUXPOWERTEK\_V01\_485(Pengcheng) |         |
| 0CH JINLANG\_CAN (Jinlang)     | 0CH LUXPOWERTEK\_V03\_485(Pengcheng) |         |
| 0DH DIDU\_CAN(Didu)          | 0DH WOW\_MOBUS (Shuori)          |         |
| 0EH SENERGYINV\_CAN          | 0EH LEOCH\_MOBUS(Leoch)          |         |
| 0FH TBB\_LITHIUM             | 0FH PYLON\_485\_F (Deye\_485)  |         |
| 10H PYLON\_V202\_CAN         | 10H AFORE(Alpha)                 |         |
| 11H GROWATT\_V109\_CAN       | 11H UPS\_AGXN(Aoguan Xinneng)         |         |
| 12H MUST\_V202\_CAN          | 12H SUNPOLO                     |         |
| 13H AFORE(Alpha)              | 13H XIONGTAO(Xiongtao)              |         |
| 14H YWT(Invt)              | 14H RONGKE(Rongke)                |         |
| 15H FUJI                     | 15H XINRUI                      |         |
| 16H SOFAR\_V21003            | 16H ELTEK(Eltek)               |         |
| 17H GT                       |                                 |         |
| 18H LEOCH\_V106              |                                 |         |

**Example 1, The only command to set to automatic identification mode:**
LCHKSUM=0A，CHKSUM=46 43 30 37，Total 24 bytes

```
7E 32 35 30 30 34 36 45 43 41 30 30 36 46 46 46 46 30 30 46 43 30 37 0D
```

Response successful, RTN=0，Total 18 bytes

```
7E 32 35 30 31 34 36 30 30 30 30 30 30 46 44 41 45 0D
```

**Example 2, Set VICTRON\_CAN and PHOCOS\_485 protocols:**
LCHKSUM=0A，CHKSUM=46 43 35 36，Total 24 bytes

```
7E 32 35 30 30 34 36 45 43 41 30 30 36 30 33 30 35 30 31 46 43 35 36 0D
```

Response successful, RTN=0，Total 18 bytes

```
7E 32 35 30 31 34 36 30 30 30 30 30 30 46 44 41 45 0D
```

**Example 3, Read current inverter protocol:**
LCHKSUM=00, CHKSUM=46 44 39 37, total 18 bytes

```
7E 32 35 30 30 34 36 45 42 30 30 30 30 46 44 39 37 0D
```

Response successful, RTN=0, total 24 bytes

```
7E 32 35 30 31 34 36 30 30 41 30 30 36 30 34 30 31 30 31 46 43 37 31 0D
```

Currently using SE_CAN protocol and PYLON_485 (Deye_485), and it is in manual mode.

**Example 4, Read Current Inverter Protocol:**
LCHKSUM=00, CHKSUM=46 44 39 37, total 18 bytes

```
7E 32 35 30 30 34 36 45 42 30 30 30 30 46 44 39 37 0D
```

Response successful, RTN=0, total 24 bytes

```
7E 32 35 30 31 34 36 30 30 41 30 30 36 30 32 30 31 30 30 46 43 37 34 0D
```

Currently using GROWATT_CAN protocol and PYLON_485 (Deye_485), and it is in automatic mode.

---

### 4.74. Enter Test Mode (FFH)

**Table A.208 Enter Test Mode Command Information**

| Sequence No.     | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count**   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**       | SOI | VER | ADR | 46H | FFH | LENGTH | COMMAND_INFO | CHKSUM | EOI |

**Note:** LENID = 02H or 04H.
COMMAND_INFO is 1 Byte, i.e., test mode command:

* COMMAND_INFO = 01H, enable current limit shielding, turn on all balancing;
* COMMAND_INFO = 02H, restore system data to default values;
* COMMAND_INFO = 03H, clear accumulated charge/discharge capacity, accumulated discharge kWh data to 0;
* COMMAND_INFO = 50H XXH, main board upgrade (XXH is the recoverable parameter selection byte, defined in Table 206);
* COMMAND_INFO = E0H / E1H / E2H / E3H / E4H /E5H / E6H, anti-theft function debugging.
  If a certain function is not available, the operation prompts failure.

**Table A.209 Recoverable Parameter Selection Explanation** 

| Value | Content                  | Remarks                                |
| :- | :----------------- | :-------------------- |
| 7     | Reserved                 |                                        |
| 6     | Reserved                 |                                        |
| 5     | Reserved                 |                                        |
| 4     | Reserved                 |                                        |
| 3     | Restore Default Protocol | 1: Recoverable 0: Non-recoverable      |
| 2     | Restore Default Protection Parameters | 1: Recoverable 0: Non-recoverable |
| 1     | Restore String Count, NTC Count | 1: Recoverable 0: Non-recoverable |
| 0     | Restore Capacity Value   | 1: Recoverable 0: Non-recoverable      |

**Table A.210 Enter Test Mode Response Information**

| Sequence No.     | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count**   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

### 4.75. Read B35 Module Information (64H)

**Table A.211 Read B35 Module Information Command Information**

| Sequence No.     | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count**   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**       | SOI | VER | ADR | 46H | 64H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.212 Read B35 Module Information Response Information**

| Sequence No.     | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count**   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

**Note:** LENID = (2*(13+N1+M1+N2+M2))H.
DATA_INFO is 13+N1+M1+N2+M2 Byte, i.e., B35 module information, types detailed in the table below.
**Table A.213 B35 Module Information Content and Transmission Order**

| Seq No. | Content                     | DATA Byte Count | Remarks                                                                                             |
| :--- | :--------------------- | :---------- | :----------------------------------------------------------------------------------------------- |
| 1    | Function Status             | 1               | 0x00: No Bluetooth WiFi function<br />0x01: Has Bluetooth WiFi function                                               |
| 2    | Module Current Status       | 1               | 0x00: Offline (Bound)<br />0x01: Network Configuration in Progress<br />0x02: Connecting to Server<br />0x03: Online<br />0x04: Unbound |
| 3    | MAC Address                 | 6 Byte          |                                                                                                  |
| 4    | Firmware Version Length     | 1 Byte          |                                                                                                  |
| 5    | Firmware Version            | N1 String       |                                                                                                  |
| 6    | License Length              | 1               | Length is 0 when no license                                                                        |
| 7    | license                | M1 String   |                                                                                                  |
| 8    | rssi                        | 1               | Unit: dbm* (-1)<br />Since DBM is negative, it needs to be converted to positive for upload                                        |
| 9    | Saved SSID Length           | 1               | Fill with 0 when not connected                                                                     |
| 10   | Saved SSID                  | N2 String       | This field does not need to be filled when not connected                                           |
| 11   | Saved Password Length       | 1               | Fill with 0 when not connected                                                                     |
| 12   | Saved Password              | M2 String       | This field does not need to be filled when not connected                                           |

*When function status is 0, it means the function is not available, subsequent data may not be parsed, and the host computer displays no such function.

---

### 4.76. Input B35 Module SN Information (65H)

**Table A.214 Input B35 Module SN Information Command Information**

| Sequence No.     | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count**   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**       | SOI | VER | ADR | 46H | 65H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

**Note:** LENID = 1CH.
COMMAND_INFO is 14 Byte.

**Table A.215 B35 Module Information Content and Transmission Order**

| Seq No. | Content               | DATA Byte Count | Remarks            |
| :--- | :--------------- | :---------- | :-------------- |
| 1       | B35 Module SN Length  | 1               | Host computer fixedly sends 13 |
| 2       | B35 Module SN         | 13              |                 |

*When the function status byte in the 64H command is 0, writing SN replies with write failure.
**Table A.216 Input B35 Module SN Information Response Information**

| Sequence No.     | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count**   | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**       | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

### 4.77. Get B35 Module SN Information (66H)

**Table A.217 Get B35 Module SN Information Command Information**

| Sequence No.     | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | 66H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.218 Get B35 Module SN Information Response Information**

| Sequence No.    | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

**Note:** LENID = 1EH.
DATA_INFO is the B35 module SN information, 15 Byte.

**Table A.219 B35 Module SN Content and Transmission Order**

| Seq. | Content             | DATA Byte Count | Remarks                                           |
| :--- | :--------------- | :---------- | :------------------------------------------------- |
| 1    | Function Status     | 1               | 0x00: No Bluetooth WiFi function<br />0x01: Has Bluetooth WiFi function |
| 2    | B35 Module SN Length | 1               | Lower computer fixedly sends 13                  |
| 3    | B35 Module SN        | 13              |                                                    |

*When function status is 0, it means no such function, the subsequent data may not be parsed, and the upper computer displays no such function.

### 4.78. Get MCU Clock Source Configuration Information (80H)

**Table A.220 Get MCU Clock Source Configuration Information Command Information**

| Sequence No.    | 1   | 2   | 3   | 4   | 5   | 6      | 7             | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :------------ | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2       | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | 80H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

**Note:** LENID = 00H.

**Table A.221 Get MCU Clock Source Configuration Information Response Information**

| Sequence No.    | 1   | 2   | 3   | 4   | 5   | 6      | 7          | 8      | 9   |
| :--------------- | :-- | :-- | :-- | :-- | :-- | :----- | :--------- | :----- | :-- |
| **Byte Count** | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2    | 2      | 1   |
| **Format**     | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

**Note:** LENID = 0AH.
DATA_INFO is the MCU clock source configuration information, 5 Byte.

**Table A.222 MCU Clock Source Configuration Content and Transmission Order**

| Seq. | Content                 | DATA Byte Count | Remarks                           |
| :--- | :----------------- | :---------- | :--------------------------------- |
| 1    | MCU Main Clock Source Type | 1           | 0x00: External crystal oscillator<br />0x01: Internal crystal oscillator |
| 2    | Crystal Oscillator Abnormal Status Flag | 1 | 0x00: Normal<br />0x01: Abnormal         |
| 3    | Switch to Internal Oscillator Count | 2 | Unit - times                    |

This instruction is only for internal production testing, not open to the public, and if reading fails, it indicates the lower computer has not implemented this function.

---

### 4.79. Protocol Pass-through Command (67H) (WiFi Bluetooth Use)

**Table A.223 Protocol Pass-through Command Information**

| Seq.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 67H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

COMMAND_INFO is the frame information to be passed through, containing the complete frame structure, N Byte, length is the pass-through protocol frame length.

**Table A.224 Protocol Pass-through Response Information**

| Seq.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 1EH.

DATA_INFO is the frame return information, containing the complete frame structure, N Byte, length is the pass-through protocol frame length.

### 4.80. Set Active Balancing Function (6AH)

**Table A.225 Set Active Balancing Command Information**

| Seq.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 64H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 02H.

COMMAND_INFO is 1 Byte, 0: Turn off active balancing 1: Turn on active balancing.

**Table A.226 Set Active Balancing Function Response Information**

| Seq.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 00H.

### 4.81. Get Active Balancing Status (6BH)

**Table A.227 Get Active Balancing Status Command Information**

| Seq.   | 1   | 2   | 3   | 4   | 5   | 6      | 7            | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | ------------ | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2      | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | 68H | LENGTH | COMMAND_INFO | CHKSUM | EOI |

Note: LENID = 00H.

**Table A.228 Get Active Balancing Status Response Information**

| Seq.   | 1   | 2   | 3   | 4   | 5   | 6      | 7         | 8      | 9   |
| ------ | --- | --- | --- | --- | --- | ------ | --------- | ------ | --- |
| Byte Count | 1   | 1   | 1   | 1   | 1   | 2      | LENID/2   | 2      | 1   |
| Format   | SOI | VER | ADR | 46H | RTN | LENGTH | DATA_INFO | CHKSUM | EOI |

Note: LENID = 02H.

DATA_INFO is 1 Byte, 0: Closed 1: Opened.

### 5. Example Description

RS232 communication is a one-to-one communication method. In practical application, the BMS will not strictly restrict the ADR field. The ADR field in the BMS response information is uploaded with the actual BMS address. Except for CID2 codes 42H and 44H, other CID2 codes are only valid for this PACK, i.e., the PACK connected to the RS232 communication cable. Communication example commands are as follows:

**Get PACK Analog Quantities:**

```
7E 32 35 30 30 34 36 34 32 45 30 30 32 30 31 46 44 33 31 0D （COMMAND = 01H）
7E 32 35 30 30 34 36 34 32 45 30 30 32 46 46 46 44 30 36 0D （COMMAND = FFH）
```

**Get PACK Alarm Quantities:**

```
7E 32 35 30 30 34 36 34 34 45 30 30 32 30 31 46 44 32 46 0D （COMMAND = 01H）
7E 32 35 30 30 34 36 34 34 45 30 30 32 46 46 46 44 30 34 0D （COMMAND = FFH）
```

**Detailed Parsing of Command Response Information:**

**Get PACK Analog Quantities Command Information:**

```
7E 32 35 30 30 34 36 34 32 45 30 30 32 46 46 46 44 30 36 0D
```

**Response Information:**

```
7E 32 35 30 30 34 36 30 30 46 30 37 41 30 30 30 31 31 30 30 44 34 32 30 44 31 34 30 44 31 33 30 44 31
33 30 44 31 33 30 44 31 33 30 44 31 33 30 44 31 33 30 44 31 31 30 44 31 32 30 44 31 33 30 44 31 31 30
44 31 31 30 44 31 32 30 44 31 30 30 44 31 33 30 36 30 42 42 37 30 42 42 37 30 42 42 38 30 42 42 36 30
42 42 33 30 42 42 44 30 30 30 30 44 31 35 35 31 32 38 45 30 33 31 33 38 38 30 30 30 30 31 33 38 38 45
33 41 43 0D
```

**Detailed Parsing of Response Information:**

```
7E（SOI）
32 35 (VER, i.e., version number 25H, V2.5)
30 30 (ADR, battery PACK address is 0)
34 36（CID1，46H）
30 30（RTN，00H）
46 30 37 41 (LENGTH, F07A, meaning LENID is 07AH, DATA_INFO length is 122 bytes, LCHKSUM is FH)
30 30 (DATA_INFO consists of INFOFLAG and DATAI, here is INFOFLAG, i.e., 00H. The following information is DATAI)
30 31 (PACK quantity, 01H)
31 30 (Number of battery cells M, i.e., 10H, which is 16 cell voltages)
30 44 34 32 (Cell voltage of string 1: 0D42H, i.e., 3394mV)
30 44 31 34 (Cell voltage of string 2: 0D14H, i.e., 3348mV)
30 44 31 33 (Cell voltage of string 3: 0D13H, i.e., 3347mV)
30 44 31 33 (Cell voltage of string 4: 0D13H, i.e., 3347mV)
30 44 31 33 (Cell voltage of string 5: 0D13H, i.e., 3347mV)
30 44 31 33 (Cell voltage of string 6: 0D13H, i.e., 3347mV)
30 44 31 33 (Cell voltage of string 7: 0D13H, i.e., 3347mV)
30 44 31 33 (Cell voltage of string 8: 0D13H, i.e., 3347mV)
30 44 31 31 (Cell voltage of string 9: 0D11H, i.e., 3345mV)
30 44 31 32 (Cell voltage of string 10: 0D12H, i.e., 3346mV)
30 44 31 33 (Cell voltage of string 11: 0D13H, i.e., 3347mV)
30 44 31 31 (Cell voltage of string 12: 0D11H, i.e., 3345mV)
30 44 31 31 (Cell voltage of string 13: 0D11H, i.e., 3345mV)
30 44 31 32 (Cell voltage of string 14: 0D12H, i.e., 3346mV)
30 44 31 30 (Cell voltage of string 15: 0D10H, i.e., 3344mV)
30 44 31 33 (Cell voltage of string 16: 0D13H, i.e., 3347mV)
30 36 (Number of monitored temperatures N, i.e., 06H, which is 6 temperatures)
30 42 42 37 (Temperature 1: 0BB7H, i.e., (2999 - 2730)/10, 26.9°C)
30 42 42 37 (Temperature 2: 0BB7H, i.e., (2999 - 2730)/10, 26.9°C)
30 42 42 38 (Temperature 3: 0BB8H, i.e., (3000 - 2730)/10, 27.0°C)
30 42 42 36 (Temperature 4: 0BB6H, i.e., (299 - 2730)/10, 26.8°C)
30 42 42 33 (Temperature 5 (MOS temperature): 0BB3H, i.e., (2995 - 2730)/10, 26.5°C)
30 42 42 44 (Temperature 6 (Ambient temperature): 0BBDH, i.e., (2994 - 2730)/10, 27.5°C)
30 30 30 30 (PACK current, 0000H, unit 10mA)
44 31 35 35 (PACK total voltage, D155H i.e., 53.589V)
31 32 38 45 (PACK remaining capacity, 128EH i.e., 47.50AH)
30 33 (Number of user-defined commands, 03H)
31 33 38 38 (PACK full charge capacity, 1388H i.e., 50.00AH)
30 30 30 30 (Charge-discharge cycle count, 0000H)
31 33 38 38 (PACK design capacity, 1388H i.e., 50.00AH)
45 33 41 43（CHKSUM，E3ACH）
0D (EOI)
```
