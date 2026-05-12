# JK BMS RS485 (55AA) Frame Protocol (Dynamic Frame 0x1620 + Setup Frame 0x161E)

**BMS**: JK_PB1A16S10P | **Firmware**: V19 | **Cells**: 16S LFP | **Frame Length**: 300 bytes + 8 bytes Modbus ACK

> Connect to the RS485B or RS485C port of the main BMS (Dial-up: 0000), and the BMS will actively and automatically send data without needing to send a request.

> Offset = 6 + Modbus register index. Frame data uses little-endian byte order (LE).

> DYNAMIC frame example: Frame type=0x1620, 52.600V, 0A idle, SOC 97%

55 AA EB 90 02 00 DC 0C DC 0C DC 0C DC 0C B9 0C DB 0C DC 0C DB 0C B9 0C DC 0C DB 0C DC 0C DC 0C DC 0C DC 0C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF 00 00 D8 0C 23 00 00 04 4A 00 47 00 48 00 45 00 49 00 46 00 4C 00 49 00 49 00 47 00 4A 00 47 00 4F 00 4D 00 4A 00 49 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 01 00 00 00 00 78 CD 00 00 00 00 00 00 00 00 00 00 FD 00 FB 00 00 00 08 00 00 00 00 61 93 7A 01 00 A0 86 01 00 00 00 00 00 14 00 00 00 64 00 00 00 72 D5 19 00 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF 00 01 00 00 00 67 27 00 00 00 00 71 49 3D 40 00 00 00 00 8C 14 00 00 00 01 01 01 00 01 01 00 34 78 01 00 00 00 00 00 03 01 FC 00 FB 00 10 27 A6 1A F6 0B 76 00 00 00 E2 2B 01 00 00 00 00 01 00 00 00 00 00 00 00 00 00 FE FF 7F DC 2F 01 01 B0 0F 07 00 00 E5 00 10 16 20 00 01 05 9A 

> SETUP frame example: Frame type=0x161E, 16S LFP, 100Ah, Cell OVP 3.65V

55 AA EB 90 01 00 D4 0D 00 00 C4 09 00 00 54 0B 00 00 42 0E 00 00 48 0D 00 00 0A 00 00 00 75 0D 00 00 8C 0A 00 00 7A 0D 00 00 48 0D 00 00 BA 09 00 00 30 75 00 00 03 00 00 00 3C 00 00 00 A0 86 01 00 2C 01 00 00 46 00 00 00 1E 00 00 00 E8 03 00 00 58 02 00 00 26 02 00 00 58 02 00 00 26 02 00 00 00 00 00 00 32 00 00 00 20 03 00 00 BC 02 00 00 10 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 A0 86 01 00 05 00 00 00 E4 0C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 A1 07 00 50 12 3C 32 18 FE FF FF FF 9F E9 6D 02 00 00 00 00 5D 00 10 16 1E 00 01 64 56 

---

# Part 1: DYNAMIC Frame (0x1620)

---

## 1. Frame Header (Offset 0-5)


| Offset | Bytes | Example Value | Type  | Meaning         | Parsed Value | Notes |
| ------ | ------ | -------- | ------- | -------------- | -------- | ------- |
| 0    | 1    | `55`   | UINT8 | Frame Header ID 1    | 0x55   | Fixed  |
| 1    | 1    | `AA`   | UINT8 | Frame Header ID 2    | 0xAA   | Fixed  |
| 2    | 1    | `EB`   | UINT8 | Function Code       | 0xEB   | Fixed  |
| 3    | 1    | `90`   | UINT8 | Sub-function Code     | 0x90   | Fixed  |
| 4    | 1    | `02`   | UINT8 | Frame Sequence Number | 0x02   | 01/02 |
| 5    | 1    | `00`   | UINT8 | Reserved         | 0x00   |       |

---

## 2. Cell Voltages (Offset 6-69)


| Offset  | Bytes | Example Value      | Type         | Meaning            | Parsed Value            | Notes                         |
| ------- | ------ | ------------- | -------------- | ----------------- | ------------------- | ------------------------------ |
| 6-7   | 2    | `DC 0C`     | UINT16le     | Cell 1 Voltage     | 3292 mV = 3.292 V | CellVol1                     |
| 8-9   | 2    | `DC 0C`     | UINT16le     | Cell 2 Voltage     | 3292 mV = 3.292 V | CellVol2                     |
| 10-11 | 2    | `DC 0C`     | UINT16le     | Cell 3 Voltage     | 3292 mV = 3.292 V | CellVol3                     |
| 12-13 | 2    | `DC 0C`     | UINT16le     | Cell 4 Voltage     | 3292 mV = 3.292 V | CellVol4                     |
| 14-15 | 2    | `B9 0C`     | UINT16le     | Cell 5 Voltage     | 3257 mV = 3.257 V | CellVol5                     |
| 16-17 | 2    | `DB 0C`     | UINT16le     | Cell 6 Voltage     | 3291 mV = 3.291 V | CellVol6                     |
| 18-19 | 2    | `DC 0C`     | UINT16le     | Cell 7 Voltage     | 3292 mV = 3.292 V | CellVol7                     |
| 20-21 | 2    | `DB 0C`     | UINT16le     | Cell 8 Voltage     | 3291 mV = 3.291 V | CellVol8                     |
| 22-23 | 2    | `B9 0C`     | UINT16le     | Cell 9 Voltage     | 3257 mV = 3.257 V | CellVol9                     |
| 24-25 | 2    | `DC 0C`     | UINT16le     | Cell 10 Voltage    | 3292 mV = 3.292 V | CellVol10                    |
| 26-27 | 2    | `DB 0C`     | UINT16le     | Cell 11 Voltage    | 3291 mV = 3.291 V | CellVol11                    |
| 28-29 | 2    | `DC 0C`     | UINT16le     | Cell 12 Voltage    | 3292 mV = 3.292 V | CellVol12                    |
| 30-31 | 2    | `DC 0C`     | UINT16le     | Cell 13 Voltage    | 3292 mV = 3.292 V | CellVol13                    |
| 32-33 | 2    | `DC 0C`     | UINT16le     | Cell 14 Voltage    | 3292 mV = 3.292 V | CellVol14                    |
| 34-35 | 2    | `DC 0C`     | UINT16le     | Cell 15 Voltage    | 3292 mV = 3.292 V | CellVol15                    |
| 36-37 | 2    | `DC 0C`     | UINT16le     | Cell 16 Voltage    | 3292 mV = 3.292 V | CellVol16                    |
| 38-69 | 32   | `00 00 ...` | UINT16le x16 | Cell 17-32 Voltage | 0 mV (Unused)     | Max support 32S, only first 16 have values for 16S |

## 3. Cell Presence Status (Offset 70-73)


| Offset  | Bytes | Example Value        | Type     | Meaning           | Parsed Value     | Notes                         |
| ------- | ------ | --------------- | ---------- | ---------------- | ------------ | ------------------------------ |
| 70-73 | 4    | `FF FF 00 00` | UINT32le | CellSta        | 0x0000FFFF | BIT[n]=1 indicates cell n+1 is present |
|       |      |               |          | Present cells: 1-16 | 16 cells   | Matches 16 cells with voltage readings     |

## 4. Voltage Statistics (Offset 74-79)


| Offset  | Bytes | Example Value  | Type     | Meaning                   | Parsed Value            | Notes                         |
| ------- | ------ | --------- | ---------- | ------------------------ | ------------------- | ------------------------------ |
| 74-75 | 2    | `D8 0C` | UINT16le | Average Voltage               | 3288 mV = 3.288 V | VolCellVolAve                |
| 76-77 | 2    | `23 00` | UINT16le | Cell Voltage Delta (max-min) | 35 mV             | 3292 - 3257 = 35 mV, unit mV |
| 78    | 1    | `00`    | UINT8    | Max Voltage Cell Number       | 0 (Cell 1)       | MaxVolCellNbr                |
| 79    | 1    | `04`    | UINT8    | Min Voltage Cell Number       | 4 (Cell 5)       | MinVolCellNbr, 0-based       |

## 5. Connection Wire Resistance (Offset 80-143)


| Offset    | Bytes | Example Value      | Type        | Meaning            | Parsed Value            | Notes            |
| --------- | ------ | ------------- | ------------- | ----------------- | ------------------- | ----------------- |
| 80-81   | 2    | `4A 00`     | INT16le     | Wire 0 Resistance     | 74 mΩ = 0.074 Ω | CellConWireRes0 |
| 82-83   | 2    | `47 00`     | INT16le     | Wire 1 Resistance     | 71 mΩ = 0.071 Ω | CellConWireRes1 |
| 84-85   | 2    | `48 00`     | INT16le     | Wire 2 Resistance     | 72 mΩ = 0.072 Ω |                 |
| 86-87   | 2    | `45 00`     | INT16le     | Wire 3 Resistance     | 69 mΩ = 0.069 Ω |                 |
| 88-89   | 2    | `49 00`     | INT16le     | Wire 4 Resistance     | 73 mΩ = 0.073 Ω |                 |
| 90-91   | 2    | `46 00`     | INT16le     | Wire 5 Resistance     | 70 mΩ = 0.070 Ω |                 |
| 92-93   | 2    | `4C 00`     | INT16le     | Wire 6 Resistance     | 76 mΩ = 0.076 Ω |                 |
| 94-95   | 2    | `49 00`     | INT16le     | Wire 7 Resistance     | 73 mΩ = 0.073 Ω |                 |
| 96-97   | 2    | `49 00`     | INT16le     | Wire 8 Resistance     | 73 mΩ = 0.073 Ω |                 |
| 98-99   | 2    | `47 00`     | INT16le     | Wire 9 Resistance     | 71 mΩ = 0.071 Ω |                 |
| 100-101 | 2    | `4A 00`     | INT16le     | Wire 10 Resistance    | 74 mΩ = 0.074 Ω |                 |
| 102-103 | 2    | `47 00`     | INT16le     | Wire 11 Resistance    | 71 mΩ = 0.071 Ω |                 |
| 104-105 | 2    | `4F 00`     | INT16le     | Wire 12 Resistance    | 79 mΩ = 0.079 Ω |                 |
| 106-107 | 2    | `4D 00`     | INT16le     | Wire 13 Resistance    | 77 mΩ = 0.077 Ω |                 |
| 108-109 | 2    | `4A 00`     | INT16le     | Wire 14 Resistance    | 74 mΩ = 0.074 Ω |                 |
| 110-111 | 2    | `49 00`     | INT16le     | Wire 15 Resistance    | 73 mΩ = 0.073 Ω |                 |
| 112-143 | 32   | `00 00 ...` | INT16le x16 | Wire 16-31 Resistance | 0 mΩ (Not connected)    | Max support 32S     |

## 6. MOS Temperature (Offset 144-145)


| Offset    | Bytes | Example Value  | Type    | Meaning      | Parsed Value              | Notes                 |
| --------- | ------ | --------- | --------- | ----------- | --------------------- | ---------------------- |
| 144-145 | 2    | `03 01` | INT16le | MOS Temperature | 259 raw → 25.9 °C | TempMos, unit 0.1°C |

## 7. Balance Wire Resistance Alarm (Offset 146-149)


| Offset    | Bytes | Example Value        | Type     | Meaning       | Parsed Value     | Notes                         |
| --------- | ------ | --------------- | ---------- | ------------ | ------------ | ------------------------------ |
| 146-149 | 4    | `00 00 00 00` | UINT32le | WireResSta | 0x00000000 | BIT[n]=1 indicates balance wire n is open circuit |

## 8. Electrical Data (Offset 150-161)


| Offset    | Bytes | Example Value        | Type     | Meaning         | Parsed Value               | Notes                             |
| --------- | ------ | --------------- | ---------- | -------------- | ---------------------- | ---------------------------------- |
| 150-153 | 4    | `78 CD 00 00` | UINT32le | Battery Total Voltage | 52600 mV = 52.600 V  | BatVol, unit mV                  |
| 154-157 | 4    | `00 00 00 00` | UINT32le | Battery Power     | 0 mW = 0.0 W         | BatWatt, unit mW                 |
| 158-161 | 4    | `00 00 00 00` | INT32le  | Battery Current     | 0 mA = 0.00 A [IDLE] | BatCur, unit mA, positive=charge negative=discharge |

## 9. Battery Temperature (Offset 162-259)


| Offset    | Bytes | Example Value  | Type    | Meaning       | Parsed Value              | Notes                  |
| --------- | ------ | --------- | --------- | ------------ | --------------------- | ----------------------- |
| 162-163 | 2    | `FD 00` | INT16le | Battery Temperature 1 | 253 raw → 25.3 °C | TempBat1, unit 0.1°C |
| 164-165 | 2    | `FB 00` | INT16le | Battery Temperature 2 | 251 raw → 25.1 °C | TempBat2, unit 0.1°C |
| 254-255 | 2    | `03 01` | INT16le | Battery Temperature 3 | 259 raw → 25.9 °C | TempBat3, unit 0.1°C |
| 256-257 | 2    | `FC 00` | INT16le | Battery Temperature 4 | 252 raw → 25.2 °C | TempBat4, unit 0.1°C |
| 258-259 | 2    | `FB 00` | INT16le | Battery Temperature 5 | 251 raw → 25.1 °C | TempBat5, unit 0.1°C |

## 10. Alarm/Protection Bits (Offset 166-169)


| Offset    | Bytes | Example Value        | Type     | Meaning       | Parsed Value     | Notes           |
| --------- | ------ | --------------- | ---------- | ------------ | ------------ | ---------------- |
| 166-169 | 4    | `00 00 08 00` | UINT32le | Alarm Bit Field | 0x00080000 | 1=Fault, 0=Normal |

**Alarm Bit Definitions (BIT 0-23):**


| BIT | Fault Name                    | Description            |
| ----- | ----------------------------- | --------------------- |
| 0   | Battery SCP                 | Battery Short Circuit Protection        |
| 1   | MOS over-temp protection    | MOS Over-temperature Protection         |
| 2   | Cell qty mismatch (NCM/LFP) | Cell Type/Quantity Mismatch |
| 3   | Cell OVP                    | Cell Over-voltage Protection        |
| 4   | Cell UVP                    | Cell Under-voltage Protection        |
| 5   | Battery OVP                 | Battery Over-voltage Protection        |
| 6   | Battery UVP                 | Battery Under-voltage Protection        |
| 7   | Charge OCP                  | Charge Over-current Protection        |
| 8   | Discharge OCP               | Discharge Over-current Protection        |
| 9   | Charge over-temp            | Charge Over-temperature Protection        |
| 10  | Aux CPU comm fault          | Aux CPU Communication Fault     |
| 11  | Cell UVP (2nd)              | Cell Under-voltage Protection (Secondary)  |
| 12  | Battery OVP (2nd)           | Battery Over-voltage Protection (Secondary)  |
| 13  | Battery UVP (2nd)           | Battery Under-voltage Protection (Secondary)  |
| 14  | Charge OCP (2nd)            | Charge Over-current Protection (Secondary)  |
| 15  | Discharge OCP (2nd)         | Discharge Over-current Protection (Secondary)  |
| 16  | Charge low-temp protection  | Charge Low-temperature Protection        |
| 17  | Discharge over-temp         | Discharge Over-temperature Protection        |
| 18  | GPS disconnected            | GPS Disconnected         |
| 19  | Password modify reminder    | Please Change Authorization Password Promptly  |
| 20  | Discharge activate failure  | Discharge Activation Failure        |
| 21  | Bat temp sensor anomaly     | Battery Temperature Sensor Anomaly  |
| 22  | Temperature sensor anomaly  | Temperature Sensor Anomaly      |
| 23  | Parallel module fault       | Parallel Module Fault        |


## 11. Balance Current (Offset 170-171)


| Offset | Bytes | Example Value | Type    | Meaning       | Parsed Value         | Remarks                |
| --------- | ------ | --------- | --------- | ---------- | ---------------- | ----------------------- |
| 170-171 | 2    | `00 00` | INT16le | Balance Current | 0 mA = 0.000 A | BalanCurrent, unit mA |

## 12. Battery Status & SOC (Offset 172-173)


| Offset | Bytes | Example Value | Type  | Meaning       | Parsed Value          | Remarks                           |
| ------ | ------ | -------- | ------- | -------------- | ----------------- | -------------------------------- |
| 172  | 1    | `00`   | UINT8 | Battery Status     | 0 (Standby/Off) | BatSta: 0=Off, 1=Charge, 2=Discharge |
| 173  | 1    | `61`   | UINT8 | Remaining SOC | 97 %            | SOCStateOfCharge               |

## 13. Capacity Data (Offset 174-189)


| Offset | Bytes | Example Value    | Type     | Meaning                      | Parsed Value              | Remarks                         |
| --------- | ------ | --------------- | ---------- | --------------------- | ------------------------- | ---------------------------- |
| 174-177 | 4    | `93 7A 01 00` | INT32le  | Remaining Capacity            | 96915 mAh = 96.915 Ah   | SOCCapRemain, unit mAh         |
| 178-181 | 4    | `A0 86 01 00` | UINT32le | Actual Battery Capacity (Full Charge) | 100000 mAh = 100.000 Ah | SOCFullChargeCap, unit mAh     |
| 182-185 | 4    | `00 00 00 00` | UINT32le | Cycle Count                   | 0 cycles                | SOCCycleCount                  |
| 186-189 | 4    | `14 00 00 00` | UINT32le | Total Cycle Capacity          | 20 mAh                  | SOCCycleCap, unit mAh          |

## 14. SOH / Pre-charge / Alarm Values / Runtime (Offset 190-201)


| Offset | Bytes | Example Value    | Type     | Meaning             | Parsed Value            | Remarks            |
| --------- | ------ | --------------- | ---------- | -------------- | --------------------- | ----------------- |
| 190     | 1    | `64`          | UINT8    | Health SOH           | 100 %                 |                   |
| 191     | 1    | `00`          | UINT8    | Pre-charge Status    | OFF (0)               | 0=Off, 1=On      |
| 192-193 | 2    | `00 00`       | UINT16le | User Alarm Value 1   | 0                     | UserAlarm1       |
| 194-197 | 4    | `72 D5 19 00` | UINT32le | Runtime              | 1693042 s = 470.3 h   | RunTime, unit seconds |
| 198     | 1    | `01`          | UINT8    | Charge MOS           | ON (1)                | 0=Off, 1=On      |
| 199     | 1    | `01`          | UINT8    | Discharge MOS        | ON (1)                | 0=Off, 1=On      |
| 200     | 1    | `00`          | UINT8    | Balance MOS          | OFF (0)               | 0=Off, 1=On      |
| 200-201 | 2    | `00 00`       | UINT16le | User Alarm Value 2   | 0                     | UserAlarm2       |

## 15. Protection Release Delay (Offset 202-213)


| Offset | Bytes | Example Value | Type     | Meaning                              | Parsed Value | Remarks       |
| --------- | ------ | --------- | ---------- | ------------------ | -------- | ------------ |
| 202-203 | 2    | `00 00` | UINT16le | Discharge Over-current Release Time  | 0 s      | TimeDeOCPR   |
| 204-205 | 2    | `00 00` | UINT16le | Discharge Short-circuit Release Time | 0 s      | TimeDeSCPR   |
| 206-207 | 2    | `00 00` | UINT16le | Charge Over-current Release Time     | 0 s      | TimeChOCPR   |
| 208-209 | 2    | `00 00` | UINT16le | Charge Short-circuit Release Time    | 0 s      | TimeChUVPR   |
| 210-211 | 2    | `00 00` | UINT16le | Cell Under-voltage Release Time      | 0 s      | TimeUVPR     |
| 212-213 | 2    | `00 00` | UINT16le | Cell Over-voltage Release Time       | 0 s      | TimeOVPR     |

## 16. Temperature Sensor Presence & Heating (Offset 214-215)


| Offset | Bytes | Example Value | Type  | Meaning                         | Parsed Value | Remarks                               |
| ------ | ------ | -------- | ------- | -------------------- | --------- | ------------------------------------ |
| 214  | 1    | `FF`   | UINT8 | Temperature Sensor Presence Status | 0xFF      | BIT[n]=1 sensor normal; BIT[n]=0 missing |
| 215  | 1    | `00`   | UINT8 | Heating Status                   | OFF (0)   | 0=Off, 1=On                          |

**Sensor Presence Bit Definition (BIT 0-5):**


| BIT | Sensor                     |
| ----- | ------------------ |
| 0   | MOS Temperature Sensor     |
| 1   | Battery Temperature Sensor 1 |
| 2   | Battery Temperature Sensor 2 |
| 3   | Battery Temperature Sensor 3 |
| 4   | Battery Temperature Sensor 4 |
| 5   | Battery Temperature Sensor 5 |

## 17. Emergency Switch / Current Correction / Sensor Voltage / Calibration (Offset 216-235)


| Offset | Bytes | Example Value    | Type      | Meaning                      | Parsed Value        | Remarks                           |
| --------- | ------ | --------------- | ----------- | -------------------- | ----------------- | -------------------------------- |
| 216-217 | 2    | `01 00`       | UINT16le  | (Reserved)                   |                   |                                  |
| 218-219 | 2    | `00 00`       | UINT16le  | Emergency Switch Time        | 0 s               | TimeEmergency, unit s            |
| 220-221 | 2    | `67 27`       | UINT16le  | Discharge Current Correction Factor | 10087       | VolBatCurCorrect                 |
| 222-223 | 2    | `00 00`       | UINT16le  | Charge Current Sensor Voltage | 0 mV              | VolChargeCur                     |
| 224-225 | 2    | `00 00`       | UINT16le  | Discharge Current Sensor Voltage | 0 mV           | VolDischargeCur                  |
| 226-229 | 4    | `71 49 3D 40` | FLOAT32le | Voltage Calibration Factor    | 2.957608          | BatVolCorrect                    |
| 230-231 | 2    | `00 00`       | UINT16le  | (Reserved/Unknown)            |                   |                                  |
| 232-233 | 2    | `00 00`       | UINT16le  | (Reserved/Unknown)            |                   |                                  |
| 234-235 | 2    | `8C 14`       | UINT16le  | Battery Voltage               | 5260 → 52.60 V    | BatVol, unit 0.01V, reg 0x00E4   |

## 18. Heating Current / Charger / System Runtime (Offset 236-253)


| Offset | Bytes | Example Value    | Type     | Meaning               | Parsed Value                       | Remarks                                        |
| --------- | ------ | --------------- | ---------- | ---------------- | ------------------------------ | --------------------------------------------- |
| 236-237 | 2    | `00 00`       | INT16le  | Heating Current       | 0 mA = 0.000 A               | HeatCurrent, unit mA                          |
| 238-243 | 6    | —            | —       | (Reserved/Unknown)    |                              |                                               |
| 244     | 1    | `01`          | UINT8    | Reserved              | —                            | RVD, reg 0x00EE                               |
| 245     | 1    | `00`          | UINT8    | Charger Plugged Status | NO (0)                      | ChargerPlugged, reg 0x00EF, 0=Unplugged 1=Plugged |
| 246-249 | 4    | `34 78 01 00` | UINT32le | System Runtime Count  | 96308 ticks = 9631 s = 2.7 h | SysRunTicks, unit 0.1s                        |

## 19. RTC / Sleep / Parallel / Fault Record (Offset 250-299)


| Offset | Bytes | Example Value     | Type     | Meaning                             | Parsed Value             | Remarks                            |
| --------- | ------ | ---------------- | ---------- | ---------------------- | ---------------------- | ------------------------------- |
| 250-253 | 4    | —               | —        | (Reserved/Unknown)                  |                         |                                   |
| 254-259 | 6    | —               | —        | Battery Temperature 3-5             | —                      | → see Section 9, reg 0x00F8/FA/FC  |
| 260-261 | 2    | —               | —        | (Reserved/Unknown)                  |                         |                                   |
| 262-265 | 4    | `A6 1A F6 0B`  | UINT32le | RTC Timestamp                       | 200664742 s            | RTC Time, calculated from 2020-01-01 |
| 266     | 1    | `76`            | UINT8    | Fault Count                         | 118                    | FaultCount                         |
| 267-269 | 3    | —               | —        | (Reserved/Unknown)                  |                         |                                   |
| 270-273 | 4    | `E2 2B 01 00`  | UINT32le | Sleep Entry Time                    | 76770 s = 21.3 h       | TimeEnterSleep, reg 0x0108        |
| 274     | 1    | `00`            | UINT8    | Parallel Current Limiting Module Status | 0 (Off)            | PCLModuleSta: 1=On, 0=Off        |
| 275     | 1    | `00`            | UINT8    | Reserved                            | —                      | RVD, reg 0x010C                  |
| 276-299 | 24   | —               | —        | (Reserved/Unknown)                  |                         |                                   |

---

## 20. Trailing Modbus ACK (Offset 300-307)


| Offset | Bytes | Example Value | Type     | Meaning             | Parsed Value            | Remarks                         |
| --------- | ------ | --------- | ---------- | --------------- | ----------------------- | -------------------------- |
| 300     | 1    | `00`    | UINT8    | Pack ID              | 0                       | 0=1st pack, 1=2nd pack       |
| 301     | 1    | `10`    | UINT8    | Modbus Function Code | 0x10 (Write Multiple)   |                              |
| 302-303 | 2    | `16 20` | UINT16   | Register Address     | 0x1620 (DYNAMIC frame)  |                              |
| 304-305 | 2    | `00 01` | UINT16   | Register Count       | 1                       |                              |
| 306-307 | 2    | `05 9A` | UINT16le | CRC                  | 0x9A05                  |                              |

---

# Part 2: SETUP Frame (0x161E)

---

## 1. Frame Header (Offset 0-5)

| Offset | Bytes | Example Value | Type  | Meaning              | Parsed Value           | Remarks                    |
| ------ | ------ | -------- | ------- | -------------- | ------------------ | ------------------------- |
| 0    | 1    | `55`   | UINT8 | Frame Header Marker 1 | 0x55               | Fixed                      |
| 1    | 1    | `AA`   | UINT8 | Frame Header Marker 2 | 0xAA               | Fixed                      |
| 2    | 1    | `EB`   | UINT8 | Function Code         | 0xEB               | Fixed                      |
| 3    | 1    | `90`   | UINT8 | Sub-function Code     | 0x90               | Fixed                      |
| 4    | 1    | `02`   | UINT8 | Frame Sequence Number | 0x02               | 01/02 |
| 5    | 1    | `00`   | UINT8 | Reserved              | 0x00               |                            |

## 2. Protection Voltage Parameters (Offset 6-49, reg 0x0000-0x0028)

| Offset | Bytes | Example Value     | Type     | Meaning                           | Parsed Value         | Remarks           |
| ------ | ------ | ---------------- | ---------- | -------------------- | ------------------ | ---------------- |
| 6-9   | 4    | `D4 0D 00 00`  | UINT32le | Sleep Entry Voltage               | 3540 → 3.540 V     | VolSmartSleep    |
| 10-13 | 4    | `C4 09 00 00`  | UINT32le | Cell Under-voltage Protection     | 2500 → 2.500 V     | VolCellUVP       |
| 14-17 | 4    | `54 0B 00 00`  | UINT32le | Cell Under-voltage Recovery Voltage | 2900 → 2.900 V   | VolCellUVPR      |
| 18-21 | 4    | `42 0E 00 00`  | UINT32le | Cell Over-voltage Protection      | 3650 → 3.650 V     | VolCellOVP       |
| 22-25 | 4    | `48 0D 00 00`  | UINT32le | Cell Over-voltage Recovery Voltage | 3400 → 3.400 V     | VolCellOVPR      |
| 26-29 | 4    | `0A 00 00 00`  | UINT32le | Balance Start Voltage Difference  | 10 → 0.010 V       | VolBalanTrig     |
| 30-33 | 4    | `75 0D 00 00`  | UINT32le | SOC=100% Voltage                  | 3445 → 3.445 V     | VolSOC100%       |
| 34-37 | 4    | `8C 0A 00 00`  | UINT32le | SOC=0% Voltage                    | 2700 → 2.700 V     | VolSOC0%         |
| 38-41 | 4    | `7A 0D 00 00`  | UINT32le | Pack Under-voltage Protection     | 3450 → 3.450 V     | VolBatUVP        |
| 42-45 | 4    | `48 0D 00 00`  | UINT32le | Pack Over-voltage Protection      | 3400 → 3.400 V     | VolBatOVP        |
| 46-49 | 4    | `BA 09 00 00`  | UINT32le | Auto Power-off Voltage            | 2490 → 2.490 V     | VolSysPwrOff     |


## III. Protection Current & Delay (Offset 50-81, reg 0x002C-0x0048)

| Offset | Bytes | Example Value   | Type     | Meaning                          | Parsed Value | Notes              |
| ------ | ------ | ---------------- | ---------- | ----------------------------------- | ------------ | -------------------- |
| 50-53 | 4    | `30 75 00 00`  | INT32le  | Continuous Charge Current           | 30000 mA    | CurBatCOC          |
| 54-57 | 4    | `03 00 00 00`  | UINT32le | Charge Overcurrent Protection Delay  | 3 s         | TIMBatCOCPDly      |
| 58-61 | 4    | `3C 00 00 00`  | UINT32le | Charge Overcurrent Protection Release | 60 s        | TIMBatCOCPRDly     |
| 62-65 | 4    | `A0 86 01 00`  | UINT32le | Continuous Discharge Current         | 100000 mA   | CurBatDcOC         |
| 66-69 | 4    | `2C 01 00 00`  | UINT32le | Discharge Overcurrent Protection Delay | 300 s       | TIMBatDcOCPDly     |
| 70-73 | 4    | `46 00 00 00`  | UINT32le | Discharge Overcurrent Protection Release | 70 s        | TIMBatDcOCPRDly    |
| 74-77 | 4    | `1E 00 00 00`  | UINT32le | Short Circuit Protection Release     | 30 s        | TIMBatSCPRDly      |
| 78-81 | 4    | `E8 03 00 00`  | UINT32le | Maximum Balance Current              | 1000 mA     | CurBalanMax        |

## IV. Temperature Protection (Offset 82-113, reg 0x004C-0x0068)

| Offset | Bytes | Example Value   | Type     | Meaning                   | Parsed Value       | Notes           |
| ------ | ------ | ---------------- | ---------- | -------------------------- | ---------------------- | ---------------- |
| 82-85 | 4    | `58 02 00 00`  | INT32le  | Charge Over-temperature Protection        | 600 → 60.0°C | TMPBatCOT      |
| 86-89 | 4    | `26 02 00 00`  | INT32le  | Charge Over-temperature Recovery         | 550 → 55.0°C | TMPBatCOTPR    |
| 90-93 | 4    | `58 02 00 00`  | INT32le  | Discharge Over-temperature Protection    | 600 → 60.0°C | TMPBatDOT      |
| 94-97 | 4    | `26 02 00 00`  | INT32le  | Discharge Over-temperature Recovery      | 550 → 55.0°C | TMPBatDOTPR    |
| 98-101 | 4   | `00 00 00 00`  | INT32le  | Charge Low-temperature Protection        | 0 → 0.0°C    | TMPBatCUT      |
| 102-105 | 4  | `32 00 00 00`  | INT32le  | Charge Low-temperature Recovery          | 50 → 5.0°C   | TMPBatCUTPR    |
| 106-109 | 4  | `20 03 00 00`  | INT32le  | MOS Over-temperature Protection          | 800 → 80.0°C | TMPMosOTP      |
| 110-113 | 4  | `BC 02 00 00`  | INT32le  | MOS Over-temperature Protection Recovery | 700 → 70.0°C | TMPMosOTPR     |

## V. Battery Configuration & Switches (Offset 114-137, reg 0x006C-0x0080)

| Offset | Bytes | Example Value   | Type     | Meaning                | Parsed Value            | Notes                         |
| ------ | ------ | ---------------- | ---------- | ----------------------- | ------------------------- | ------------------------------ |
| 114-117 | 4  | `10 00 00 00`  | UINT32le | Cell Count              | 16 cells               | CellCount                    |
| 118-121 | 4  | `01 00 00 00`  | UINT32le | Charge Switch           | ON (1)                 | BatChargeEN: 1=ON, 0=OFF     |
| 122-125 | 4  | `01 00 00 00`  | UINT32le | Discharge Switch        | ON (1)                 | BatDisChargeEN: 1=ON, 0=OFF  |
| 126-129 | 4  | `01 00 00 00`  | UINT32le | Balance Switch          | ON (1)                 | BalanEN: 1=ON, 0=OFF         |
| 130-133 | 4  | `A0 86 01 00`  | UINT32le | Battery Design Capacity | 100000 mAh = 100 Ah   | CapBatCell, unit: mAh         |
| 134-137 | 4  | `05 00 00 00`  | UINT32le | Short Circuit Protection Delay | 5 us            | SCPDelay, unit: us            |

## VI. Balance Start Voltage (Offset 138-141, reg 0x0084)

| Offset | Bytes | Example Value   | Type     | Meaning              | Parsed Value               | Notes         |
| ------ | ------ | ---------------- | ---------- | --------------------- | ---------------------------- | -------------- |
| 138-141 | 4  | `E4 0C 00 00`  | UINT32le | Balance Start Voltage | 3300 mV = 3.300 V          | VolStartBalan |

## VII. Connection Wire Resistance Calibration (Offset 142-269, reg 0x0088-0x0104)

| Offset | Bytes | Example Value   | Type          | Meaning                       | Parsed Value | Notes                     |
| ------ | ------ | ---------------- | --------------- | ------------------------------ | ------------ | -------------------------- |
| 142-269 | 128 | `00 00 00 00...` | INT32le x32   | Wire 0-31 Resistance Calibration | All 0     | CellConWireRes0-31, unit: uΩ |

## VIII. Device Configuration (Offset 270-287, reg 0x0108-0x0118)

| Offset | Bytes | Example Value   | Type     | Meaning             | Parsed Value | Notes            |
| ------ | ------ | ---------------- | ---------- | -------------------- | ------------ | ------------------ |
| 270-273 | 4  | `00 00 00 00`  | UINT32le | Device Address        | 0           | DevAddr, unit: H   |
| 274-277 | 4  | `00 00 00 00`  | UINT32le | Precharge Delay       | 0 s         | TIMPrecharge      |
| 278-281 | 4  | —              | —        | (Reserved)            | —           |                   |
| 282-283 | 2  | `00 00`        | UINT16le | Function Bit Field    | 0x0000      | reg 0x0114        |
| 284-285 | 2  | —              | —        | (Reserved)            | —           |                   |
| 286     | 1  | `00`           | UINT8    | Smart Sleep Time      | 0 H         | TIMSmartSleep     |

**Function Bit Field BIT Definitions (reg 0x0114):**

| BIT | Name               | Meaning                                  |
|-----|-------------------|------------------------------------------|
| 0   | HeatEN            | Heating Enable (1=ON, 0=OFF)             |
| 1   | DisableTempSensor | Temperature Sensor Disable (1=Disabled, 0=Normal) |
| 2   | GPS Heartbeat     | GPS Heartbeat Packet (1=ON, 0=OFF)       |
| 3   | Port Switch       | Communication Port Switch (1=RS485, 0=CAN) |
| 4   | LCD Always On     | LCD Always On (1=ON, 0=OFF)              |
| 5   | Special Charger   | Special Charger Recognition (1=ON, 0=OFF) |
| 6   | SmartSleep        | Smart Sleep (1=ON, 0=OFF)                |
| 7   | DisablePCLModule  | Disable Parallel Current Limiting (1=Disabled, 0=Normal) |
| 8   | TimedStoredData   | Timed Data Storage (1=ON, 0=OFF)         |
| 9   | ChargingFloatMode | Charge Float Mode (1=ON, 0=OFF)          |

## IX. Trailing Modbus ACK (Offset 300-307)

> The SETUP frame tail data has 24 more bytes than the DYNAMIC frame (32 bytes total tail), the last 8 bytes are the Modbus ACK.

| Offset   | Bytes | Example Value  | Type     | Meaning            | Parsed Value              | Notes                       |
| -------- | ------ | --------------- | ---------- | ------------------- | ------------------------- | ---------------------------- |
| 300-323 | 24   | `00 00 20 A1...` | —       | Extra Data          | —                       | SETUP frame specific, content TBD |
| 324     | 1    | `00`           | UINT8    | Pack ID             | 0                       | 0=1st pack                  |
| 325     | 1    | `10`           | UINT8    | Modbus Function Code | 0x10 (Write Multiple)   |                              |
| 326-327 | 2    | `16 1E`        | UINT16   | Register Address     | 0x161E (SETUP frame)    |                              |
| 328-329 | 2    | `00 01`        | UINT16   | Register Count       | 1                       |                              |
| 330-331 | 2    | `64 56`        | UINT16le | CRC Checksum         | 0x5664                  |                              |

---

## Appendix A: DYNAMIC Frame Complete Example

```
55 AA EB 90 02 00                    ← Frame Header
DC 0C DC 0C DC 0C DC 0C B9 0C DB 0C ← Cell 1-6 (3292,3292,3292,3292,3257,3291 mV)
DC 0C DB 0C B9 0C DC 0C DB 0C DC 0C ← Cell 7-12
DC 0C DC 0C DC 0C DC 0C DC 0C 00 00 ← Cell 13-16 + Cell 17-18=0
... (Cell 19-32 All 0) ...
FF FF 00 00                          ← CellSta (16 cell present)
D8 0C 23 00 00 04                    ← Avg 3288mV, delta=35mV, maxCell=0, minCell=4
4A 00 47 00 48 00 45 00             ← Wire 0-3 (74,71,72,69 mΩ)
49 00 46 00 4C 00 49 00             ← Wire 4-7
49 00 47 00 4A 00 47 00             ← Wire 8-11
4F 00 4D 00 4A 00 49 00             ← Wire 12-15
... (Wire 16-31 All 0) ...
03 01                                ← MOS temp: 25.9°C
00 00 00 00                          ← Wire alarm: All Normal
78 CD 00 00                          ← Total Voltage: 52600 mV
00 00 00 00                          ← Power: 0 mW
00 00 00 00                          ← Current: 0 mA
FD 00 FB 00                          ← Temp1:25.3°C, Temp2:25.1°C
00 00 08 00                          ← Alarm: BIT19 (Password modify reminder)
00 00                                ← Balance Current: 0 mA
00 61                                ← Status:0(Standby), SOC:97%
93 7A 01 00                          ← Remaining Capacity: 96915 mAh
A0 86 01 00                          ← Full Charge Capacity: 100000 mAh
00 00 00 00                          ← Cycle Count: 0
14 00 00 00                          ← Cycle Capacity: 20 mAh
64 00                                ← SOH:100%, Pre-charge:OFF
00 00                                ← UserAlarm1: 0
72 D5 19 00                          ← Runtime: 1693042 s
01 01 00                             ← Charge MOS:ON, Discharge MOS:ON, Balance MOS:OFF
00 00                                ← UserAlarm2: 0
... (Protection Delays All 0) ...
FF 00                                ← Sensors:All Present, Heating:OFF
... ...
34 78 01 00                          ← SysRunTicks: 96308
... ...
03 01 FC 00 FB 00                    ← Temp3:25.9°C, Temp4:25.2°C, Temp5:25.1°C
... ...
                                   ← Trailing ACK:
00 10 16 20 00 01 05 9A              ← Pack=0, FC=0x10, Reg=0x1620, Cnt=1, CRC=0x9A05
```

## Appendix B: SETUP Frame Complete Example

```
55 AA EB 90 01 00                    ← Frame Header
D4 0D 00 00                          ← Sleep Entry Voltage: 3540 mV (3.540V)
C4 09 00 00                          ← Cell UVP: 2500 mV (2.500V)
54 0B 00 00                          ← Cell UVP Recovery: 2900 mV (2.900V)
42 0E 00 00                          ← Cell OVP: 3650 mV (3.650V)
48 0D 00 00                          ← Cell OVP Recovery: 3400 mV (3.400V)
0A 00 00 00                          ← Balance Start Voltage Diff: 10 mV (0.010V)
75 0D 00 00                          ← SOC=100% Voltage: 3445 mV (3.445V)
8C 0A 00 00                          ← SOC=0% Voltage: 2700 mV (2.700V)
7A 0D 00 00                          ← Pack UVP: 3450 mV (3.450V)
48 0D 00 00                          ← Pack OVP: 3400 mV (3.400V)
BA 09 00 00                          ← Auto Power-off Voltage: 2490 mV (2.490V)
30 75 00 00                          ← Continuous Charge Current: 30000 mA (30A)
03 00 00 00                          ← Charge OCP Delay: 3 s
3C 00 00 00                          ← Charge OCP Release: 60 s
A0 86 01 00                          ← Continuous Discharge Current: 100000 mA (100A)
2C 01 00 00                          ← Discharge OCP Delay: 300 s
46 00 00 00                          ← Discharge OCP Release: 70 s
1E 00 00 00                          ← Short Circuit Protection Release: 30 s
E8 03 00 00                          ← Max Balance Current: 1000 mA
58 02 00 00                          ← Charge Over-temp Protection: 600 (60.0°C)
26 02 00 00                          ← Charge Over-temp Recovery: 550 (55.0°C)
58 02 00 00                          ← Discharge Over-temp Protection: 600 (60.0°C)
26 02 00 00                          ← Discharge Over-temp Recovery: 550 (55.0°C)
00 00 00 00                          ← Charge Low-temp Protection: 0 (0.0°C)
32 00 00 00                          ← Charge Low-temp Recovery: 50 (5.0°C)
20 03 00 00                          ← MOS Over-temp Protection: 800 (80.0°C)
BC 02 00 00                          ← MOS Over-temp Protection Recovery: 700 (70.0°C)
10 00 00 00                          ← Cell Count: 16S
01 00 00 00                          ← Charge Switch: ON
01 00 00 00                          ← Discharge Switch: ON
01 00 00 00                          ← Balance Switch: ON
A0 86 01 00                          ← Battery Design Capacity: 100000 mAh (100 Ah)
05 00 00 00                          ← Short Circuit Protection Delay: 5 us
E4 0C 00 00                          ← Balance Start Voltage: 3300 mV (3.300V)
... (Wire 0-31 Calibration All 0) ...
00 00 00 00                          ← Device Address: 0
00 00 00 00                          ← Precharge Delay: 0 s
00 00                                ← Function Bit Field: 0x0000 (All OFF)
00                                   ← Smart Sleep Time: 0 H
...                                    Trailing 24 bytes extra data + ACK:
00 00 20 A1 07 00 50 12 3C 32 18 FE FF FF FF 9F E9 6D 02 00 00 00 00 5D
00 10 16 1E 00 01 64 56              ← Pack=0, FC=0x10, Reg=0x161E, Cnt=1, CRC=0x5664
```


## Appendix C: Trigger Commands

**Request DYNAMIC Frame (0x1620):**

```
01 10 16 20 00 01 02 00 00 D6 F1   (Pack 1)
02 10 16 20 00 01 02 00 00 E6 61   (Pack 2)
```

**Request SETUP Frame (0x161E):**

```
01 10 16 1E 00 01 02 00 00 77 31   (Pack 1)
02 10 16 1E 00 01 02 00 00 47 A1   (Pack 2)
```

- Function Code: 0x10 (Write Multiple Registers)
- Write Value: 0x0000
- Returns: 55AA frame (300 bytes) + trailing data + Modbus ACK
- SETUP frame ends with 24 more bytes of trailing data than DYNAMIC frames
