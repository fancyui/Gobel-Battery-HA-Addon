# JK BMS RS485 Protocol Reference

> **Firmware**: 9.04 (JK_PB1A16S10P, 16S LFP) | **HW**: 19H | **Frame format**: JK Proprietary 55AA

---

## 1. Communication Overview

The JK BMS uses a **hybrid protocol** over RS485:

| Mechanism | Description |
|-----------|-------------|
| **Data Query** | Modbus FC `0x10` (Write Multiple Registers) with value `0x0000` — triggers the BMS to respond with a JK proprietary **55AA data frame** |
| **Alarm Query** | Modbus FC `0x03` (Read Holding Registers) — standard Modbus RTU response |
| **Frame Header** | All data frames start with `55 AA` magic bytes |

Standard Modbus FC `0x03` reads of registers `0x1200`–`0x1420` return **Illegal Data Address** (`01 83 02 C0 F1`) on this firmware. Only the FC `0x10` write-trigger + FC `0x03` alarm mechanism works.

---

## 2. Modbus Query Commands

### 2.1 Data Query Commands (FC 0x10)

These commands write `0x0000` to a register, triggering the BMS to respond with a 55AA frame.

| Query Type | Register | Command Hex | Response Type |
|------------|----------|-------------|---------------|
| Static Data | `0x161C` | `01 10 16 1C 00 01 02 00 00 D3 CD` | 55AA Frame (Trame 1) |
| Setup/Config | `0x161E` | `01 10 16 1E 00 01 02 00 00 D2 2F` | 55AA Frame (Trame 2) |
| Dynamic Data | `0x1620` | `01 10 16 20 00 01 02 00 00 D6 F1` | 55AA Frame (Trame 3) |

**Command structure breakdown** (using `0x1620` as example):

| Byte Position | Value | Meaning |
|---------------|-------|---------|
| 0 | `01` | Slave address (default: 1) |
| 1 | `10` | Function code: Write Multiple Registers |
| 2–3 | `16 20` | Register address (big-endian) |
| 4–5 | `00 01` | Quantity: 1 register |
| 6 | `02` | Byte count: 2 bytes |
| 7–8 | `00 00` | Data value (write zero to trigger response) |
| 9–10 | `D6 F1` | CRC16 Modbus (little-endian) |

### 2.2 Alarm Query Command (FC 0x03)

| Register | Command Hex | Response Type |
|----------|-------------|---------------|
| `0x12A0` | `01 03 12 A0 00 02 C0 3F` | Standard Modbus RTU (9 bytes) |

---

## 3. 55AA Frame: Dynamic Data (Trame 3, register `0x1620`)

Frame size: **300 bytes** (after stripping trailing Modbus ACK).

### 3.1 Frame Header

| Offset | Length | Type | Field | Description |
|--------|--------|------|-------|-------------|
| 0 | 1 byte | `uint8` | Frame magic | `0x55` — start marker |
| 1 | 1 byte | `uint8` | Frame magic | `0xAA` — start marker |
| 2 | 1 byte | `uint8` | — | `0xEB` (fixed) |
| 3 | 1 byte | `uint8` | — | `0x90` (fixed) |
| 4 | 1 byte | `uint8` | Pack ID | Battery pack number |
| 5 | 1 byte | `uint8` | — | `0x00` (reserved) |

### 3.2 Cell Data

| Offset | Length | Type | Count | Field | Scale | Unit |
|--------|--------|------|-------|-------|-------|------|
| 6–37 | 2 bytes each | `uint16le` | ×16 | Cell voltages | Raw | mV |
| 38–79 | — | — | — | _Reserved / unknown_ | — | — |
| 80–111 | 2 bytes each | `int16le` | ×16 | Cell wire resistance | Raw | mΩ |

**Cell voltage array details:**

| Cell # | Offset | Bytes |
|--------|--------|-------|
| Cell 1 | 6 | 6–7 |
| Cell 2 | 8 | 8–9 |
| ... | ... | ... |
| Cell 16 | 36 | 36–37 |

**Cell resistance array details:**

| Cell # | Offset | Bytes |
|--------|--------|-------|
| Cell 1 | 80 | 80–81 |
| Cell 2 | 82 | 82–83 |
| ... | ... | ... |
| Cell 16 | 110 | 110–111 |

### 3.3 Temperature Sensors

| Offset | Length | Type | Field | Scale | Unit |
|--------|--------|------|-------|-------|------|
| 144 | 2 bytes | `int16le` | MOS temperature | ÷10 | °C |
| 162 | 2 bytes | `int16le` | Battery temp sensor 1 | ÷10 | °C |
| 164 | 2 bytes | `int16le` | Battery temp sensor 2 | ÷10 | °C |
| 254 | 2 bytes | `int16le` | Battery temp sensor 3 | ÷10 | °C |
| 258 | 2 bytes | `int16le` | Battery temp sensor 4 | ÷10 | °C |

Valid range for all temperature sensors: **-50°C to +150°C** (raw: -500 to 1500).

### 3.4 Electrical Parameters

| Offset | Length | Type | Field | Scale | Unit |
|--------|--------|------|-------|-------|------|
| 150 | 4 bytes | `uint32le` | Total voltage (high precision) | Raw | mV |
| 154 | 4 bytes | `uint32le` | Total power | Raw | mW |
| 158 | 4 bytes | `int32le` | Total current | Raw | mA |
| 170 | 2 bytes | `int16le` | Balance current | Raw | mA |
| 172 | 1 byte | `uint8` | Balance action flag | — | — |
| 234 | 2 bytes | `uint16le` | Total voltage (standard precision) | ÷100 | V |

**Note on voltage:** Offset 150 provides mV-level precision (e.g. `53129` → 53.129V). Offset 234 is a fallback with 0.01V precision (e.g. `5312` → 53.12V). The parser prefers offset 150 when available.

### 3.5 Battery Status

| Offset | Length | Type | Field | Scale | Unit |
|--------|--------|------|-------|-------|------|
| 173 | 1 byte | `uint8` | State of Charge (SOC) | Raw | % |
| 174 | 4 bytes | `uint32le` | Remaining capacity | ÷1000 | Ah |
| 178 | 4 bytes | `uint32le` | Full/Nominal capacity | ÷1000 | Ah |
| 182 | 4 bytes | `uint32le` | Cycle count | Raw | cycles |
| 186 | 4 bytes | `uint32le` | Cycle capacity | ÷1000 | Ah |
| 190 | 1 byte | `uint8` | State of Health (SOH) | Raw | % |
| 194 | 4 bytes | `uint32le` | Total runtime | Raw | seconds |

### 3.6 MOSFET Status

| Offset | Length | Type | Field | Values |
|--------|--------|------|-------|--------|
| 198 | 1 byte | `uint8` | Charge MOS | `0` = OFF, `1` = ON |
| 199 | 1 byte | `uint8` | Discharge MOS | `0` = OFF, `1` = ON |
| 200 | 1 byte | `uint8` | Balance MOS | `0` = OFF, `1` = ON |

### 3.7 Fault/Diagnostic

| Offset | Length | Type | Field | Scale |
|--------|--------|------|-------|-------|
| 266 | 1 byte | `uint8` | Fault record count | Raw count |

---

## 4. 55AA Frame: Static Data (Trame 1, register `0x161C`)

### 4.1 Device Information

| Offset | Length | Type | Field | Example |
|--------|--------|------|-------|---------|
| 6–18 | 13 bytes | ASCII | BMS model name | `JK_PB1A16S10P` |
| 22–24 | 3 bytes | ASCII | Hardware version | `19H` |
| 30–34 | 5 bytes | ASCII | Software version | `9.04` |
| 46–58 | 13 bytes | ASCII | Serial number | `504185745002899` |
| 78–85 | 8 bytes | ASCII | Manufacturing date | `250619` |

---

## 5. Alarm Register (`0x12A0`)

**Query**: Modbus FC `0x03`, register `0x12A0`, count `2` (4 bytes = 32-bit bitfield).

### 5.1 Modbus Response Format

| Byte | Value | Meaning |
|------|-------|---------|
| 0 | `01` | Slave address |
| 1 | `03` | Function code (Read Holding Registers) |
| 2 | `04` | Byte count (4 bytes of alarm data) |
| 3–6 | varies | 32-bit alarm value (big-endian) |
| 7–8 | varies | CRC16 Modbus |

### 5.2 Alarm Bit Definitions (32-bit bitfield)

| Bit | Alarm Description | Category |
|-----|-------------------|----------|
| 0 | Balancing resistance too high | Warning |
| 1 | MOS over-temperature protection | Protection |
| 2 | Number of cells does not match parameter | Configuration |
| 3 | Abnormal current sensor | Fault |
| 4 | Cell over-voltage protection | Protection |
| 5 | Battery over-voltage protection | Protection |
| 6 | Overcurrent charge protection | Protection |
| 7 | Charge short-circuit protection | Protection |
| 8 | Over-temperature charge protection | Protection |
| 9 | Low temperature charge protection | Protection |
| 10 | Internal communication anomaly | Fault |
| 11 | Cell under-voltage protection | Protection |
| 12 | Battery under-voltage protection | Protection |
| 13 | Overcurrent discharge protection | Protection |
| 14 | Discharge short-circuit protection | Protection |
| 15 | Over-temperature discharge protection | Protection |
| 16 | Charge MOS anomaly | Fault |
| 17 | Discharge MOS anomaly | Fault |
| 18 | GPS disconnected | Warning |
| 19 | Please modify the authorization password in time | Warning |
| 20 | Discharge activation failure | Warning |
| 21 | Battery over-temperature alarm | Warning |
| 22 | Temperature sensor anomaly | Fault |
| 23 | Parallel module anomaly | Fault |

Bit value: `0` = inactive/normal, `1` = alarm active.

---

## 6. Complete Frame Map (Dynamic Data, 300 bytes)

```
Offset  Len  Type        Field                    Scale
──────  ───  ──────────  ───────────────────────  ──────────
0       2    uint8×2     55AA Magic              55 AA
2       1    uint8       Fixed byte              EB
3       1    uint8       Fixed byte              90
4       1    uint8       Pack ID                 —
5       1    uint8       Reserved                00
6       32   uint16le×16 Cell voltages           mV
38      42   —           Reserved                —
80      32   int16le×16  Cell wire resistance    mΩ
112     32   —           Reserved                —
144     2    int16le     MOS temperature          ÷10 °C
146     4    —           Reserved                —
150     4    uint32le    Total voltage (high)     mV
154     4    uint32le    Total power              mW
158     4    int32le     Total current            mA
162     2    int16le     Battery temp sensor 1    ÷10 °C
164     2    int16le     Battery temp sensor 2    ÷10 °C
166     4    —           Reserved                —
170     2    int16le     Balance current          mA
172     1    uint8       Balance action flag      —
173     1    uint8       SOC                      %
174     4    uint32le    Remaining capacity       ÷1000 Ah
178     4    uint32le    Full capacity            ÷1000 Ah
182     4    uint32le    Cycle count              cycles
186     4    uint32le    Cycle capacity           ÷1000 Ah
190     1    uint8       SOH                      %
191     3    —           Reserved                —
194     4    uint32le    Total runtime            seconds
198     1    uint8       Charge MOS state         bool
199     1    uint8       Discharge MOS state      bool
200     1    uint8       Balance MOS state        bool
201     33   —           Reserved                —
234     2    uint16le    Total voltage (std)      ÷100 V
236     18   —           Reserved                —
254     2    int16le     Battery temp sensor 3    ÷10 °C
258     2    int16le     Battery temp sensor 4    ÷10 °C
260     6    —           Reserved                —
266     1    uint8       Fault record count       —
267     33   —           Trailing / padding       —
──────  ───  ──────────  ───────────────────────  ──────────
Total: 300 bytes
```

---

## 7. Real-World Example: 16S LFP Battery (Pack 2, Idle)

This example is from a live capture of a **JK_PB1A16S10P** (HW 19H, FW 9.04) 16-cell LiFePO4 battery at rest. The complete raw response (308 bytes) consists of a 300-byte 55AA frame followed by an 8-byte Modbus ACK.

### 7.1 Raw Hex Data (308 bytes total)

```
55 AA EB 90 02 00    ← 6-byte 55AA header (Pack ID=2)
DB 0C DB 0C DB 0C DC 0C C3 0C DC 0C DB 0C DC 0C    ← Cells 1-8 (uint16le mV)
C4 0C DB 0C DB 0C DC 0C DC 0C DC 0C DC 0C DC 0C    ← Cells 9-16 (uint16le mV)
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ← Reserved (42 bytes)
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 FF FF 00 00 D9 0C 18 00
00 04
49 00 46 00 47 00 44 00 48 00 46 00 4C 00 49 00    ← R1-R8 (int16le mΩ)
49 00 46 00 49 00 46 00 4E 00 4C 00 4A 00 48 00    ← R9-R16 (int16le mΩ)
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ← Reserved
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0F 01 00 00 00 00 8C CD 00 00 00 00 00 00 00 00    ← MOS temp + V total + Power + Current
00 00 04 01 04 01 00 00 08 00 00 00 00 62 F1 7C    ← T1,T2 + Balance + SOC + Remain cap
01 00 A0 86 01 00 00 00 00 00 92 00 00 00 64 00    ← Full cap + Cycles + Cycle cap + SOH
00 00 F2 6A 15 00 01 01 00 00 00 00 00 00 00 00    ← Runtime + MOS states
00 00 00 00 00 00 FF 00 01 00 00 00 67 27 00 00    ← ...
00 00 71 49 3D 40 00 00 00 00 8E 14 00 00 00 01    ← V std
01 01 00 01 01 00 26 9F 0A 00 00 00 00 00 0F 01    ← T3
07 01 04 01 59 27 BD BF E4 0B 6E 00 00 00 50 54    ← T4 + Faults
00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 FE
FF 7F DC 2F 01 01 B0 0F 07 00 00 CC

01 10 16 20 00 01 04 4B    ← Modbus ACK (8 bytes)
```

### 7.2 Field-by-Field Decoding

#### Header (offset 0-5)

| Offset | Bytes | Type | Field | Raw | Decoded |
|--------|-------|------|-------|-----|---------|
| 0-1 | `55 AA` | magic | Frame header | — | Valid 55AA frame |
| 2 | `EB` | uint8 | Fixed | 235 | — |
| 3 | `90` | uint8 | Fixed | 144 | — |
| 4 | `02` | uint8 | Pack ID | 2 | Pack #2 |
| 5 | `00` | uint8 | Reserved | 0 | — |

#### Cell Voltages (offset 6-37, uint16le x16, mV)

| Offset | Bytes | Raw | Decoded | Offset | Bytes | Raw | Decoded |
|--------|-------|-----|---------|--------|-------|-----|---------|
| 6-7 | `DB 0C` | 3291 | 3.291 V | 22-23 | `C4 0C` | 3268 | 3.268 V |
| 8-9 | `DB 0C` | 3291 | 3.291 V | 24-25 | `DB 0C` | 3291 | 3.291 V |
| 10-11 | `DB 0C` | 3291 | 3.291 V | 26-27 | `DB 0C` | 3291 | 3.291 V |
| 12-13 | `DC 0C` | 3292 | 3.292 V | 28-29 | `DC 0C` | 3292 | 3.292 V |
| 14-15 | `C3 0C` | 3267 | 3.267 V | 30-31 | `DC 0C` | 3292 | 3.292 V |
| 16-17 | `DC 0C` | 3292 | 3.292 V | 32-33 | `DC 0C` | 3292 | 3.292 V |
| 18-19 | `DB 0C` | 3291 | 3.291 V | 34-35 | `DC 0C` | 3292 | 3.292 V |
| 20-21 | `DC 0C` | 3292 | 3.292 V | 36-37 | `DC 0C` | 3292 | 3.292 V |

Summary: **Sum=52617 mV (52.617 V)**, Max=3292 mV (Cell 4), Min=3267 mV (Cell 5), **Diff=25 mV** (well balanced)

#### Cell Wire Resistance (offset 80-111, int16le x16, mΩ)

| Offset | Bytes | Raw | Offset | Bytes | Raw |
|--------|-------|-----|--------|-------|-----|
| 80-81 | `49 00` | 73 mΩ | 96-97 | `49 00` | 73 mΩ |
| 82-83 | `46 00` | 70 mΩ | 98-99 | `46 00` | 70 mΩ |
| 84-85 | `47 00` | 71 mΩ | 100-101 | `49 00` | 73 mΩ |
| 86-87 | `44 00` | 68 mΩ | 102-103 | `46 00` | 70 mΩ |
| 88-89 | `48 00` | 72 mΩ | 104-105 | `4E 00` | 78 mΩ |
| 90-91 | `46 00` | 70 mΩ | 106-107 | `4C 00` | 76 mΩ |
| 92-93 | `4C 00` | 76 mΩ | 108-109 | `4A 00` | 74 mΩ |
| 94-95 | `49 00` | 73 mΩ | 110-111 | `48 00` | 72 mΩ |

All 16 valid: range 68-78 mΩ, **avg = 72.4 mΩ**

#### Temperature Sensors

| Offset | Bytes | Type | Field | Raw | Decoded |
|--------|-------|------|-------|-----|---------|
| 144-145 | `0F 01` | int16le | MOS Temperature | 271 | **27.1 °C** |
| 162-163 | `04 01` | int16le | Battery Temp 1 | 260 | **26.0 °C** |
| 164-165 | `04 01` | int16le | Battery Temp 2 | 260 | **26.0 °C** |
| 254-255 | `0F 01` | int16le | Battery Temp 3 | 271 | **27.1 °C** |
| 258-259 | `04 01` | int16le | Battery Temp 4 | 260 | **26.0 °C** |

#### Electrical Parameters

| Offset | Bytes | Type | Field | Raw | Decoded |
|--------|-------|------|-------|-----|---------|
| 150-153 | `8C CD 00 00` | uint32le | Total Voltage | 52620 mV | **52.620 V** |
| 154-157 | `00 00 00 00` | uint32le | Power | 0 mW | **0.000 kW** (idle) |
| 158-161 | `00 00 00 00` | int32le | Current | 0 mA | **0.00 A** (idle) |
| 170-171 | `00 00` | int16le | Balance Current | 0 mA | **0.00 A** |
| 172 | `00` | uint8 | Balance Action | 0 | — |

Note: Cell voltage sum (52617 mV) vs uint32le total (52620 mV) differ by only 3 mV — well within measurement tolerance.

#### Battery Status

| Offset | Bytes | Type | Field | Raw | Decoded |
|--------|-------|------|-------|-----|---------|
| 173 | `62` | uint8 | SOC | 98 | **98 %** |
| 174-177 | `F1 7C 01 00` | uint32le | Remaining Capacity | 97521 mAh | **97.5 Ah** |
| 178-181 | `A0 86 01 00` | uint32le | Full Capacity | 100000 mAh | **100.0 Ah** |
| 182-185 | `00 00 00 00` | uint32le | Cycle Count | 0 | **0 cycles** |
| 186-189 | `92 00 00 00` | uint32le | Cycle Capacity | 146 mAh | **0.1 Ah** |
| 190 | `64` | uint8 | SOH | 100 | **100 %** |
| 194-197 | `F2 6A 15 00` | uint32le | Total Runtime | 1403634 s | **389.9 h (16.2 days)** |
| 234-235 | `8E 14` | uint16le | Voltage (std) | 5262 | **52.62 V** |

#### MOSFET Status

| Offset | Byte | Field | Value | State |
|--------|------|-------|-------|-------|
| 198 | `01` | Charge MOS | 1 | **ON** |
| 199 | `01` | Discharge MOS | 1 | **ON** |
| 200 | `00` | Balance MOS | 0 | OFF |

#### Diagnostics

| Offset | Byte | Field | Value |
|--------|------|-------|-------|
| 266 | `6E` | Fault Record Count | **110** |

#### Modbus ACK (trailing 8 bytes)

| Byte | Value | Meaning |
|------|-------|---------|
| 0 | `01` | Slave address |
| 1 | `10` | Function code (Write Multiple Registers) |
| 2-3 | `16 20` | Register address (0x1620) |
| 4-5 | `00 01` | Quantity (1 register) |
| 6-7 | `04 4B` | CRC16 Modbus |

### 7.3 Complete Parsed Result (JSON)

```json
{
  "pack_id": 2,
  "cell_voltages": [3291, 3291, 3291, 3292, 3267, 3292, 3291, 3292,
                    3268, 3291, 3291, 3292, 3292, 3292, 3292, 3292],
  "cell_voltage_sum_mv": 52617,
  "cell_voltage_max": 3292,
  "cell_voltage_min": 3267,
  "cell_voltage_diff_mv": 25,
  "cell_resistances_mohm": [73, 70, 71, 68, 72, 70, 76, 73,
                             73, 70, 73, 70, 78, 76, 74, 72],
  "voltage_v": 52.620,
  "power_kw": 0.0,
  "current_a": 0.0,
  "temp_mos_c": 27.1,
  "temp_bat1_c": 26.0,
  "temp_bat2_c": 26.0,
  "temp_bat3_c": 27.1,
  "temp_bat4_c": 26.0,
  "balance_current_a": 0.0,
  "soc_pct": 98,
  "remain_capacity_ah": 97.5,
  "full_capacity_ah": 100.0,
  "cycle_count": 0,
  "cycle_capacity_ah": 0.1,
  "soh_pct": 100,
  "total_runtime_s": 1403634,
  "total_runtime_days": 16.2,
  "charge_mos": true,
  "discharge_mos": true,
  "balance_mos": false,
  "fault_count": 110
}
```

### 7.4 Key Observations from This Capture

1. **Battery at rest**: 0A current, 0W power — all 16 cells balanced within 25 mV
2. **Two voltage fields agree**: uint32le (52.620V) matches cell sum (52.617V) within 3 mV
3. **All 16 wire resistances valid**: range 68-78 mΩ, averaging 72.4 mΩ — healthy connections
4. **Relatively new battery**: 0 cycles, 100% SOH, only 16.2 days of runtime
5. **Charge + Discharge MOSFETs both ON**: BMS is in normal operating state, ready to charge or discharge
6. **Response format**: 300-byte 55AA frame + 8-byte Modbus ACK = 308 bytes total TCP payload

---

## 8. Data Type Reference

| Type | Width | Byte Order | Description |
|------|-------|------------|-------------|
| `uint8` | 1 byte | — | Unsigned 8-bit integer |
| `uint16le` | 2 bytes | Little-endian | Unsigned 16-bit integer |
| `int16le` | 2 bytes | Little-endian | Signed 16-bit integer |
| `uint32le` | 4 bytes | Little-endian | Unsigned 32-bit integer |
| `int32le` | 4 bytes | Little-endian | Signed 32-bit integer |
| ASCII | variable | — | ASCII-encoded string, null-padded |

### Python Unpacking Reference

```python
import struct

# uint16le (e.g., cell voltage at offset 6)
cell_mv = struct.unpack_from('<H', data, offset)[0]   # mV

# int16le (e.g., temperature at offset 162)
temp_raw = struct.unpack_from('<h', data, offset)[0]
temp_c = temp_raw / 10.0                               # °C

# uint32le (e.g., voltage at offset 150)
voltage_mv = struct.unpack_from('<I', data, offset)[0]
voltage_v = voltage_mv / 1000.0                        # V

# int32le (e.g., current at offset 158)
current_ma = struct.unpack_from('<i', data, offset)[0]
current_a = current_ma / 1000.0                        # A
```

---

## 9. CRC16 Modbus Reference

**Polynomial**: `0xA001` (reflected)  
**Initial value**: `0xFFFF`  
**Output**: Little-endian appended to frame

```python
def crc16_modbus(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc
```
