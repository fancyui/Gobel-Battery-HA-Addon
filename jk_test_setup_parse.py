#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JK BMS 55AA SETUP frame parser (register 0x161E).
Firmware: 9.04 (JK_PB1A16S10P, 16S LFP).

Frame type: 0x01 = SETUP frame, corresponds to protocol 0x1000 register map.
Offset formula: frame_offset = 6 + register_index
"""

import datetime
import struct
import sys
sys.stdout.reconfigure(encoding='utf-8')

HEX_DATA = (
    "55 AA EB 90 01 00 D4 0D 00 00 C4 09 00 00 54 0B 00 00 "
    "42 0E 00 00 48 0D 00 00 0A 00 00 00 75 0D 00 00 8C 0A "
    "00 00 7A 0D 00 00 48 0D 00 00 BA 09 00 00 30 75 00 00 "
    "03 00 00 00 3C 00 00 00 A0 86 01 00 2C 01 00 00 46 00 "
    "00 00 1E 00 00 00 E8 03 00 00 58 02 00 00 26 02 00 00 "
    "58 02 00 00 26 02 00 00 00 00 00 00 32 00 00 00 20 03 "
    "00 00 BC 02 00 00 10 00 00 00 01 00 00 00 01 00 00 00 "
    "01 00 00 00 A0 86 01 00 05 00 00 00 E4 0C 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 A1 07 00 "
    "50 12 3C 32 18 FE FF FF FF 9F E9 6D 02 00 00 00 00 5D "
    "00 10 16 1E 00 01 64 56"
)


def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str.replace(" ", ""))


def sep(title):
    print(f"\n{'='*70}\n  {title}\n{'='*70}")


raw = hex_to_bytes(HEX_DATA)
frame = raw[:300]
ack = raw[300:]

u8  = lambda off: frame[off]
u16 = lambda off: struct.unpack_from('<H', frame, off)[0]
s16 = lambda off: struct.unpack_from('<h', frame, off)[0]
u32 = lambda off: struct.unpack_from('<I', frame, off)[0]
s32 = lambda off: struct.unpack_from('<i', frame, off)[0]

# ============================================================================
# HEADER
# ============================================================================
frame_type = "SETUP" if frame[4] == 0x01 else "DYNAMIC" if frame[4] == 0x02 else f"UNKNOWN(0x{frame[4]:02X})"
print(f"55AA SETUP Frame: {len(frame)} bytes + {len(ack)}-byte Modbus ACK = {len(raw)} bytes total")
print(f"  Header:       55 AA")
print(f"  Function:     0x{frame[2]:02X} (EB)  Sub: 0x{frame[3]:02X} (90)")
print(f"  Frame Type:   0x{frame[4]:02X} ({frame_type})  [01=SETUP, 02=DYNAMIC]")
print(f"  Reserved:     0x{frame[5]:02X}")

# ============================================================================
# ACK
# ============================================================================
# SETUP frame may have variable-length trailing data. Extract last 8 bytes as ACK.
if len(ack) >= 8:
    # Use last 8 bytes as Modbus ACK
    ack_tail = ack[-8:]
    pack_id  = ack_tail[0]
    func     = ack_tail[1]
    reg_addr = (ack_tail[2] << 8) | ack_tail[3]
    reg_cnt  = (ack_tail[4] << 8) | ack_tail[5]
    crc      = struct.unpack_from('<H', ack_tail, 6)[0]
    print(f"\n  Trailing data ({len(ack)} bytes): {' '.join(f'{b:02X}' for b in ack)}")
    print(f"  Last 8 bytes (Modbus ACK): {' '.join(f'{b:02X}' for b in ack_tail)}")
    print(f"  Pack ID:      {pack_id}")
    print(f"  Function:     0x{func:02X}")
    print(f"  Reg addr:     0x{reg_addr:04X} ({'SETUP' if reg_addr==0x161E else 'DYNAMIC' if reg_addr==0x1620 else '?'})")
    print(f"  Count:        0x{reg_cnt:04X}")
    print(f"  CRC:          0x{crc:04X}")
else:
    pack_id = 0
    func = 0
    reg_addr = 0
    reg_cnt = 0
    crc = 0

# ============================================================================
# Helper: register offset
# ============================================================================
def reg(r):
    """Convert register index to frame offset: offset = 6 + r"""
    return 6 + r

# ============================================================================
# 1. Battery Type & Protection Voltages (reg 0x0000-0x0028)
# ============================================================================
sep("1. BATTERY TYPE & PROTECTION VOLTAGES (reg 0x0000-0x0028)")

fields_v = [
    (0x0000, "VolSmartSleep",    "进入休眠电压",        0.001, "V"),
    (0x0004, "VolCellUVP",       "单体欠压保护",         0.001, "V"),
    (0x0008, "VolCellUVPR",      "单体欠压恢复电压",     0.001, "V"),
    (0x000C, "VolCellOVP",       "单体过压保护",         0.001, "V"),
    (0x0010, "VolCellOVPR",      "单体过压恢复电压",     0.001, "V"),
    (0x0014, "VolBalanTrig",     "均衡开启压差",         0.001, "V"),
    (0x0018, "VolSOC100%",       "SOC=100%电压",         0.001, "V"),
    (0x001C, "VolSOC0%",         "SOC=0%电压",           0.001, "V"),
    (0x0020, "VolBatUVP",        "整组欠压保护",         0.001, "V"),
    (0x0024, "VolBatOVP",        "整组过压保护",         0.001, "V"),
    (0x0028, "VolSysPwrOff",     "自动关机电压",         0.001, "V"),
]
for r, name, desc, scale, unit in fields_v:
    raw_v = u32(reg(r))
    val = raw_v * scale
    print(f"  reg 0x{r:04X}  off={reg(r):3d}  {raw_v:8d} raw  →  {val:8.3f} {unit}  [{desc}]  ({name})")

# ============================================================================
# 2. Protection Currents & Delays (reg 0x002C-0x0048)
# ============================================================================
sep("2. PROTECTION CURRENTS & DELAYS (reg 0x002C-0x0048)")

fields_c = [
    (0x002C, "CurBatCOC",       "持续充电电流",         "mA", True),
    (0x0030, "TIMBatCOCPDly",   "充电过流保护延迟",     "s",  False),
    (0x0034, "TIMBatCOCPRDly",  "充电过流保护解除",     "s",  False),
    (0x0038, "CurBatDcOC",      "持续放电电流",         "mA", False),
    (0x003C, "TIMBatDcOCPDly",  "放电过流保护延迟",     "s",  False),
    (0x0040, "TIMBatDcOCPRDly", "放电过流保护解除",     "s",  False),
    (0x0044, "TIMBatSCPRDly",   "短路保护解除",         "s",  False),
    (0x0048, "CurBalanMax",     "最大均衡电流",         "mA", False),
]
for r, name, desc, unit, is_signed in fields_c:
    raw_v = s32(reg(r)) if is_signed else u32(reg(r))
    print(f"  reg 0x{r:04X}  off={reg(r):3d}  {raw_v:8d} {unit:>4s}  [{desc}]  ({name})")

# ============================================================================
# 3. Temperature Protections (reg 0x004C-0x0068)
# ============================================================================
sep("3. TEMPERATURE PROTECTIONS (reg 0x004C-0x0068)")

fields_t = [
    (0x004C, "TMPBatCOT",    "充电过温保护",     True),
    (0x0050, "TMPBatCOTPR",  "充电过温恢复",     True),
    (0x0054, "TMPBatDOT",    "放电过温保护",     True),
    (0x0058, "TMPBatDOTPR",  "放电过温恢复",     True),
    (0x005C, "TMPBatCUT",    "充电低温保护",     True),
    (0x0060, "TMPBatCUTPR",  "充电低温恢复",     True),
    (0x0064, "TMPMosOTP",    "MOS过温保护",      True),
    (0x0068, "TMPMosOTPR",   "MOS过温保护恢复",  True),
]
for r, name, desc, is_signed in fields_t:
    raw_v = s32(reg(r)) if is_signed else u32(reg(r))
    print(f"  reg 0x{r:04X}  off={reg(r):3d}  {raw_v:6d} raw  →  {raw_v/10:7.1f} °C  [{desc}]  ({name})")

# ============================================================================
# 4. Battery Capacity & Switches (reg 0x006C-0x0080)
# ============================================================================
sep("4. BATTERY CAPACITY & SWITCHES (reg 0x006C-0x0080)")

fields_b = [
    (0x006C, "CellCount",       "单体数量",         "串"),
    (0x0070, "BatChargeEN",     "充电开关",         "bool"),
    (0x0074, "BatDisChargeEN",  "放电开关",         "bool"),
    (0x0078, "BalanEN",         "均衡开关",         "bool"),
    (0x007C, "CapBatCell",      "电池设计容量",     "mAh"),
    (0x0080, "SCPDelay",        "短路保护延时",     "us"),
]
for r, name, desc, unit in fields_b:
    raw_v = u32(reg(r))
    if unit == "bool":
        print(f"  reg 0x{r:04X}  off={reg(r):3d}  {raw_v:8d} raw  →  {'ON' if raw_v else 'OFF':>5s}    [{desc}]  ({name})")
    elif unit == "串":
        print(f"  reg 0x{r:04X}  off={reg(r):3d}  {raw_v:8d} raw  →  {raw_v} {unit}    [{desc}]  ({name})")
    else:
        print(f"  reg 0x{r:04X}  off={reg(r):3d}  {raw_v:8d} raw  →  {raw_v} {unit}  [{desc}]  ({name})")

# ============================================================================
# 5. Balance Start Voltage (reg 0x0084)
# ============================================================================
sep("5. BALANCE START VOLTAGE (reg 0x0084)")
raw_b = u32(reg(0x0084))
print(f"  reg 0x0084  off={reg(0x0084):3d}  {raw_b:8d} raw  →  {raw_b} mV = {raw_b/1000:.3f} V  [均衡起始电压]  (VolStartBalan)")

# ============================================================================
# 6. Wire Resistance Calibration (reg 0x0088-0x0104)
# ============================================================================
sep("6. WIRE RESISTANCE CALIBRATION (reg 0x0088-0x0104)")
# INT32, unit uΩ
for i in range(32):
    r = 0x0088 + i * 4
    raw_w = s32(reg(r))
    if raw_w != 0:
        print(f"  reg 0x{r:04X}  off={reg(r):3d}  {raw_w:8d} uΩ = {raw_w/1000:.3f} mΩ  [Wire{i}]  (CellConWireRes{i})")

# Count zeros
zero_count = sum(1 for i in range(32) if s32(reg(0x0088 + i * 4)) == 0)
if zero_count > 0:
    print(f"  ... ({zero_count} wires with 0 uΩ calibration)")

# ============================================================================
# 7. Device Config (reg 0x0108-0x0118)
# ============================================================================
sep("7. DEVICE CONFIG (reg 0x0108-0x0118)")

# 0x0108: DevAdd (设备地址)
dev_addr = u32(reg(0x0108))
print(f"  reg 0x0108  off={reg(0x0108):3d}  {dev_addr:8d} raw  →  {dev_addr}  [设备地址]  (DevAdd)")

# 0x010C: TIMPrecharge (预充延时)
prechg_t = u32(reg(0x010C))
print(f"  reg 0x010C  off={reg(0x010C):3d}  {prechg_t:8d} raw  →  {prechg_t} s  [预充延时]  (TIMPrecharge)")

# 0x0114: Bit field
bitfield = u16(reg(0x0114))
print(f"\n  reg 0x0114  off={reg(0x0114):3d}  0x{bitfield:04X}  [功能位字段]")
BIT_DEFS_0114 = [
    (0,  "HeatEN",              "加热使能"),
    (1,  "DisableTempSensor",   "温度传感器禁用"),
    (2,  "GPS Heartbeat",       "GPS心跳包"),
    (3,  "Port Switch",         "通讯端口切换 (1=RS485, 0=CAN)"),
    (4,  "LCD Always On",       "显示屏常亮"),
    (5,  "Special Charger",     "专用充电器识别"),
    (6,  "SmartSleep",          "智能休眠"),
    (7,  "DisablePCLModule",    "禁用并联限流"),
    (8,  "TimedStoredData",     "数据定时存储"),
    (9,  "ChargingFloatMode",   "充电浮充模式"),
]
for bit, name, desc in BIT_DEFS_0114:
    state = "ON" if bitfield & (1 << bit) else "OFF"
    print(f"    BIT{bit}: [{state:>3s}]  {desc}  ({name})")

# 0x0118: TIMSmartSleep (智能休眠时间)
sleep_t = u8(reg(0x0118))
print(f"\n  reg 0x0118  off={reg(0x0118):3d}  {sleep_t:8d} raw  →  {sleep_t} H  [智能休眠时间]  (TIMSmartSleep)")

# ============================================================================
# 8. Unmapped / Reserved (offset 280-299)
# ============================================================================
sep("8. UNMAPPED / RESERVED (offset 280-299)")
# Registers beyond 0x0118 are not in the 0x1000 section
# Check for non-zero bytes
non_zero = []
for off in range(reg(0x0118)+1, 300):
    if frame[off] != 0:
        non_zero.append((off, frame[off]))
if non_zero:
    for off, val in non_zero:
        print(f"  off={off:3d}  0x{val:02X} ({val})")
else:
    print(f"  All zero (no unmapped data)")

# ============================================================================
# FULL HEX DUMP
# ============================================================================
sep("FULL 300-BYTE 55AA SETUP FRAME HEX DUMP")
for row_start in range(0, 300, 16):
    row_bytes = frame[row_start:min(row_start+16, len(frame))]
    hex_str = ' '.join(f'{b:02X}' for b in row_bytes)
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row_bytes)
    print(f"  {row_start:04X}: {hex_str:48s}  {ascii_str}")

# ============================================================================
# SUMMARY
# ============================================================================
sep("SUMMARY")
print(f"  55AA Frame Type:               0x{frame[4]:02X} ({frame_type})")
print(f"  Pack ID (in ACK):              {pack_id}")
print(f"  Register base (from ACK):      0x{reg_addr:04X}")
print(f"  Battery config:                {u32(reg(0x006C))}S LFP")
print(f"  Cell OVP:                      {u32(reg(0x000C))/1000:.2f} V")
print(f"  Cell UVP:                      {u32(reg(0x0004))/1000:.2f} V")
print(f"  Battery design capacity:       {u32(reg(0x007C))} mAh = {u32(reg(0x007C))/1000:.1f} Ah")
print(f"  Charge enable:                 {'ON' if u32(reg(0x0070)) else 'OFF'}")
print(f"  Discharge enable:              {'ON' if u32(reg(0x0074)) else 'OFF'}")
print(f"  Balance enable:                {'ON' if u32(reg(0x0078)) else 'OFF'}")
print(f"  Device address:                {u32(reg(0x0108))}")
