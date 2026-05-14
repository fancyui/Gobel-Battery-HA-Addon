#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete JK BMS 55AA frame parser (dynamic frame, register 0x1620).
Firmware: 9.04 (JK_PB1A16S10P, 16S LFP).

Offsets marked [VERIFIED] match jkbms_rs485.py parse_jkbms_55aa_frame()
and are confirmed working by the user.
Offsets marked [DOC] are derived from JK-BMS-RS485-MODBUS-20250611.md V1.1
register table (frame_offset = 6 + register_index) but may differ in
actual 55AA frame layout -- these need live verification.
"""

import datetime
import struct
import sys
sys.stdout.reconfigure(encoding='utf-8')

HEX_DATA = (
    "55 AA EB 90 02 00 DC 0C DC 0C DC 0C DC 0C B9 0C DB 0C DC 0C DB 0C "
    "B9 0C DC 0C DB 0C DC 0C DC 0C DC 0C DC 0C DC 0C 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 FF FF 00 00 D8 0C 23 00 00 04 4A 00 47 00 48 00 45 00 "
    "49 00 46 00 4C 00 49 00 49 00 47 00 4A 00 47 00 4F 00 4D 00 4A 00 "
    "49 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00 03 01 00 00 00 00 78 CD 00 00 "
    "00 00 00 00 00 00 00 00 FD 00 FB 00 00 00 08 00 00 00 00 61 93 7A "
    "01 00 A0 86 01 00 00 00 00 00 14 00 00 00 64 00 00 00 72 D5 19 00 "
    "01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF 00 01 00 00 00 "
    "67 27 00 00 00 00 71 49 3D 40 00 00 00 00 8C 14 00 00 00 01 01 01 "
    "00 01 01 00 34 78 01 00 00 00 00 00 03 01 FC 00 FB 00 10 27 A6 1A "
    "F6 0B 76 00 00 00 E2 2B 01 00 00 00 00 01 00 00 00 00 00 00 00 00 "
    "00 FE FF 7F DC 2F 01 01 B0 0F 07 00 00 E5 00 10 16 20 00 01 05 9A"
)


def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str.replace(" ", ""))


# ============================================================================
# ALARM BIT DEFINITIONS (register 0x00A0, UINT32le at frame offset 166)
# ============================================================================
ALARM_BITS = {
    0:  ("Battery SCP",                  "电池短路保护"),
    1:  ("MOS over-temp protection",     "MOS过温保护"),
    2:  ("Cell qty mismatch (NCM/LFP)",  "电芯类型/数量不匹配"),
    3:  ("Cell OVP",                     "单体过压保护"),
    4:  ("Cell UVP",                     "单体欠压保护"),
    5:  ("Battery OVP",                  "整组过压保护"),
    6:  ("Battery UVP",                  "整组欠压保护"),
    7:  ("Charge OCP",                   "充电过流保护"),
    8:  ("Discharge OCP",                "放电过流保护"),
    9:  ("Charge over-temp",             "充电过温保护"),
    10: ("Aux CPU comm fault",           "辅助CPU通讯故障"),
    11: ("Cell UVP (2nd)",               "单体欠压保护(次级)"),
    12: ("Battery OVP (2nd)",            "整组过压保护(次级)"),
    13: ("Battery UVP (2nd)",            "整组欠压保护(次级)"),
    14: ("Charge OCP (2nd)",             "充电过流保护(次级)"),
    15: ("Discharge OCP (2nd)",          "放电过流保护(次级)"),
    16: ("Charge low-temp protection",   "充电低温保护"),
    17: ("Discharge over-temp",          "放电过温保护"),
    18: ("GPS disconnected",             "GPS断开连接"),
    19: ("Password modify reminder",      "请及时修改授权密码"),
    20: ("Discharge activate failure",   "放电开启失败"),
    21: ("Bat temp sensor anomaly",      "电池温度传感器异常"),
    22: ("Temperature sensor anomaly",   "温度传感器异常"),
    23: ("Parallel module fault",        "并机模块故障"),
}

# Temperature sensor presence bits (register 0x00D0, UINT8)
SENSOR_PRESENCE = {
    0: "MOS temp sensor",
    1: "Bat temp sensor 1",
    2: "Bat temp sensor 2",
    3: "Bat temp sensor 3",
    4: "Bat temp sensor 4",
    5: "Bat temp sensor 5",
}

BAT_STATUS_MAP = {0: "Standby/Off", 1: "Charging", 2: "Discharging"}


def sep(title):
    print(f"\n{'='*70}\n  {title}\n{'='*70}")


def u8(off):  return frame[off]
def u16(off): return struct.unpack_from('<H', frame, off)[0]
def s16(off): return struct.unpack_from('<h', frame, off)[0]
def u32(off): return struct.unpack_from('<I', frame, off)[0]
def s32(off): return struct.unpack_from('<i', frame, off)[0]
def f32(off): return struct.unpack_from('<f', frame, off)[0]

# ============================================================================
raw = hex_to_bytes(HEX_DATA)
frame = raw[:300]
ack   = raw[300:]

# ==== HEADER ====
print(f"55AA Frame: {len(frame)} bytes + {len(ack)}-byte Modbus ACK = {len(raw)} bytes total")
print(f"  Header:       55 AA")
print(f"  Function:     0x{frame[2]:02X} (EB)  Sub: 0x{frame[3]:02X} (90)")
frame_type = "DYNAMIC" if frame[4] == 0x02 else "SETUP" if frame[4] == 0x01 else f"UNKNOWN(0x{frame[4]:02X})"
print(f"  Frame Type:   0x{frame[4]:02X} ({frame_type})  [02=DYNAMIC, 01=SETUP]")
print(f"  Reserved:     0x{frame[5]:02X}")

# ==== 1. CELL VOLTAGES [VERIFIED] offset 6-37, 16 x UINT16le mV ====
sep("1. CELL VOLTAGES  (offset 6-37, register 0x0000-0x001E) [VERIFIED]")
cells = []
for i in range(32):
    off = 6 + i * 2
    mv = u16(off)
    if mv > 0:
        cells.append((i+1, mv))
active_cells = [v for _, v in cells]
if active_cells:
    for idx, mv in cells:
        bar = "#" * int(mv / 3300 * 30)
        print(f"  Cell{idx:2d}  off={6+(idx-1)*2:3d}  reg=0x{(idx-1)*2:04X}  {mv:5d} mV = {mv/1000:.3f} V  {bar}")
    print(f"\n  Active cells:  {len(active_cells)}")
    print(f"  Range:         {min(active_cells)} - {max(active_cells)} mV  (delta {max(active_cells)-min(active_cells)} mV)")
    print(f"  Total:         {sum(active_cells)/1000:.3f} V")
    print(f"  Average:       {sum(active_cells)//len(active_cells)} mV")

# ==== 2. CELL STATUS / PRESENCE [DOC] offset 70, reg 0x0040, UINT32le ====
sep("2. CELL STATUS / PRESENCE  (offset 70, reg 0x0040, CellSta) [DOC]")
cell_sta = u32(70)
print(f"  Raw:  0x{cell_sta:08X}  binary: {cell_sta:032b}")
print(f"  Protocol doc: 'CellSta' BIT[n]=1 = cell n present")
present_cells = [i+1 for i in range(32) if cell_sta & (1 << i)]
print(f"  Cells present: {present_cells}  ({len(present_cells)} cells)")

# ==== 3. VOLTAGE STATISTICS [DOC] offset 74-79, reg 0x0044-0x0049 ====
sep("3. CELL VOLTAGE STATISTICS  (offset 74-79, reg 0x0044-0x0049) [DOC]")
avg_v_raw  = u16(74)
max_v_raw  = u16(76)
max_cell   = u8(78)
min_cell   = u8(79)
print(f"  Average voltage:     {avg_v_raw} mV  ({avg_v_raw/1000:.3f} V)  [reg 0x0044]")
cell_delta = max(active_cells) - min(active_cells)
print(f"  Cell voltage delta:  {max_v_raw} mV  (max-min = {cell_delta} mV)  [reg 0x0046]")
print(f"  Max voltage cell #:  {max_cell}  [reg 0x0048]")
print(f"  Min voltage cell #:  {min_cell}  [reg 0x0049 -- note: cell 5 has min={min(active_cells)}mV]")

# ==== 4. WIRE RESISTANCES [VERIFIED] offset 80-111, 16 x INT16le mohm ====
sep("4. WIRE RESISTANCES  (offset 80-111, reg 0x004A-0x0068) [VERIFIED]")
for i in range(32):
    off = 80 + i * 2
    if off + 2 > len(frame):
        break
    r = s16(off)
    if 0 <= r <= 1000:
        print(f"  Wire{i:2d}  off={off:3d}  reg=0x{0x004A+i*2:04X}  {r:4d} mohm = {r/1000:.3f} ohm")

# ==== 5. MOS TEMPERATURE [VERIFIED] offset 144, reg 0x008A, INT16le /10 ====
sep("5. MOS TEMPERATURE  (offset 144, reg 0x008A) [VERIFIED]")
mos_t_raw = s16(144)
print(f"  MOS temp:  {mos_t_raw/10:.1f} C  (raw int16 = {mos_t_raw}, /10)")

# ==== 6. WIRE / BALANCE WIRE RESISTANCE ALARM STATUS ====
#     reg 0x008C (doc says base 0x1200, but 55AA frame packs it at offset 6+0x8C=146)
sep("6. BALANCE WIRE RESISTANCE ALARM  (offset 146, reg 0x008C) [DOC]")
wire_alarm = u32(146)
print(f"  Raw:  0x{wire_alarm:08X}")
print(f"  BIT[n]=1 -> balance wire n has alarm")
alarm_wires = [n for n in range(32) if wire_alarm & (1 << n)]
if alarm_wires:
    print(f"  Alarm wires: {alarm_wires}")
else:
    print(f"  All balance wires normal (no alarm)")

# ==== 7. ELECTRICAL [VERIFIED] offset 150-161 ====
sep("7. ELECTRICAL DATA  (offset 150-161, reg 0x0090/0x1200, 0x0094, 0x0098) [VERIFIED]")
v_mv = u32(150)
p_mw = u32(154)
i_ma = s32(158)
direction = "CHARGING" if i_ma > 0 else "DISCHARGING" if i_ma < 0 else "IDLE"
print(f"  Total voltage:   {v_mv} mV  = {v_mv/1000:.3f} V  (uint32le, reg 0x0090 base 0x1200)")
print(f"  Power:           {p_mw} mW  = {p_mw/1000:.1f} W = {p_mw/1000000:.3f} kW  (uint32le, reg 0x0094)")
print(f"  Current:         {i_ma} mA  = {i_ma/1000:.2f} A  [{direction}]  (int32le, reg 0x0098)")

# ==== 8. TEMPERATURES [VERIFIED] offset 162,164,254,258,262 ====
sep("8. BATTERY TEMPERATURES  [VERIFIED]")
temp_entries = [
    (162, 0x009C, "Battery temp 1"),
    (164, 0x009E, "Battery temp 2"),
    (254, 0x00F8, "Battery temp 3"),
    (256, 0x00FA, "Battery temp 4"),
    (258, 0x00FC, "Battery temp 5"),
]
for off, reg, label in temp_entries:
    if off + 2 <= len(frame):
        raw_t = s16(off)
        if -500 < raw_t < 1500:
            print(f"  {label:20s}  off={off:3d}  reg=0x{reg:04X}  {raw_t/10:.1f} C  (raw={raw_t})")
        else:
            print(f"  {label:20s}  off={off:3d}  reg=0x{reg:04X}  N/A (raw={raw_t}, out of range)")

# ==== 9. ALARM BITS [VERIFIED] offset 166, reg 0x00A0, UINT32le ====
sep("9. ALARM / PROTECTION BITS  (offset 166, reg 0x00A0, UINT32le) [VERIFIED]")

# Raw byte dump around alarm area
print("  Raw bytes around offset 166:")
for row_start in range(156, 212, 16):
    row_bytes = frame[row_start:min(row_start+16, len(frame))]
    hex_str = ' '.join(f'{b:02X}' for b in row_bytes)
    markers = []
    for i in range(len(row_bytes)):
        ao = row_start + i
        if ao == 150: markers.append("<-VmV")
        if ao == 154: markers.append("<-PmW")
        if ao == 158: markers.append("<-ImA")
        if ao == 162: markers.append("<-T1")
        if ao == 164: markers.append("<-T2")
        if ao == 166: markers.append("<-ALARM***")
        if ao == 170: markers.append("<-BalA")
        if ao == 172: markers.append("<-BatSta")
        if ao == 173: markers.append("<-SOC")
        if ao == 174: markers.append("<-RemainCap")
        if ao == 178: markers.append("<-FullCap")
        if ao == 182: markers.append("<-Cycles")
        if ao == 186: markers.append("<-CycleCap")
        if ao == 190: markers.append("<-SOH")
        if ao == 191: markers.append("<-Prechg")
        if ao == 194: markers.append("<-Runtime")
        if ao == 198: markers.append("<-ChgMOS")
        if ao == 199: markers.append("<-DchMOS")
        if ao == 200: markers.append("<-BalMOS")
    m = '  '.join(markers)
    print(f"  {row_start:04X}: {hex_str:48s}  {m}")

print()
alarm_raw = u32(166)
print(f"  Raw alarm value:  0x{alarm_raw:08X}  ({alarm_raw})")
print(f"  Binary:           {alarm_raw:032b}")
print()

active_alarms = []
for bit in range(24):
    if alarm_raw & (1 << bit):
        en_name, cn_name = ALARM_BITS.get(bit, (f"Reserved bit {bit}", ""))
        active_alarms.append((bit, en_name, cn_name))

if active_alarms:
    print(f"  Active alarms ({len(active_alarms)}):")
    for bit, en, cn in active_alarms:
        print(f"    BIT{bit:2d}  [FAULT]  {en}")
        print(f"           ({cn})")
else:
    print("  No active alarms (all normal)")

# ==== 10. BALANCE CURRENT [VERIFIED] offset 170, reg 0x00A4, INT16le mA ====
sep("10. BALANCE CURRENT  (offset 170, reg 0x00A4) [VERIFIED]")
bal_ma = s16(170)
print(f"  Balance current:  {bal_ma} mA = {bal_ma/1000:.3f} A")
# No special note needed: CellSta = cell presence per protocol, independent of balance current

# ==== 11. BATTERY STATUS + SOC [VERIFIED] offset 172-173, reg 0x00A6 ====
sep("11. BATTERY STATUS & SOC  (offset 172-173, reg 0x00A6) [VERIFIED]")
bat_sta = u8(172)
soc_val = u8(173)
print(f"  Battery status:     {bat_sta} ({BAT_STATUS_MAP.get(bat_sta, 'UNKNOWN')})  [reg 0x00A6, BatSta]")
print(f"  SOC:               {soc_val} %                                          [reg 0x00A7, SOCStateOfCharge]")

# ==== 12. CAPACITIES [VERIFIED] offset 174,178,182,186 ====
sep("12. CAPACITIES  [VERIFIED]")
remain_mah = u32(174)   # reg 0x00A8, SOCCapRemain
full_mah   = u32(178)   # reg 0x00AC, SOCFullChargeCap
cycles     = u32(182)   # reg 0x00B0, SOCCycleCount
cycle_cap  = u32(186)   # reg 0x00B4, SOCCycleCap
print(f"  Remain capacity:    {remain_mah} mAh = {remain_mah/1000:.3f} Ah  (off=174, reg 0x00A8, SOCCapRemain)")
print(f"  Full capacity:      {full_mah} mAh = {full_mah/1000:.3f} Ah  (off=178, reg 0x00AC, SOCFullChargeCap)")
print(f"  Cycle count:        {cycles}                    (off=182, reg 0x00B0, SOCCycleCount)")
print(f"  Cycle capacity:     {cycle_cap} mAh                (off=186, reg 0x00B4, SOCCycleCap)")

# ==== 13. SOH / PRECHARGE / USER ALARM / RUNTIME [VERIFIED+DOC] ====
sep("13. SOH, PRECHARGE, USER ALARMS, RUNTIME  [VERIFIED+DOC]")
soh      = u8(190)      # reg 0x00B8
prechg   = u8(191)      # reg 0x00B9
user_al1 = u16(192)     # reg 0x00BA  UserAlarm1
runtime  = u32(194)     # reg 0x00BC  (protocol says UINT16, but actually UINT32)
chg_mos  = u8(198)      # reg 0x00C0  Charge status
dch_mos  = u8(199)      # reg 0x00C1  Discharge status
bal_mos  = u8(200)      # reg 0x00C2  UserAlarm2 low byte (or Balance MOS)
user_al2 = u16(200)     # reg 0x00C2  UserAlarm2
print(f"  SOH:               {soh} %        (off=190, reg 0x00B8)")
print(f"  Precharge:         {'ON' if prechg else 'OFF'}         (off=191, reg 0x00B9)")
print(f"  UserAlarm1:        {user_al1}           (off=192, reg 0x00BA) [DOC]")
print(f"  Runtime:           {runtime} s = {runtime/3600:.1f} h  (off=194, reg 0x00BC, as UINT32)")
print(f"  Charge MOS:        {'ON' if chg_mos else 'OFF'}          (off=198, reg 0x00C0)")
print(f"  Discharge MOS:     {'ON' if dch_mos else 'OFF'}          (off=199, reg 0x00C1)")
print(f"  Balance MOS/byte:  {'ON' if bal_mos else 'OFF'}          (off=200, reg 0x00C2 low byte)")
print(f"  UserAlarm2(reg):   {user_al2}           (off=200, reg 0x00C2, as UINT16) [DOC]")

# ==== 14. PROTECTION DELAY TIMES [DOC] offset 202-212, reg 0x00C4-0x00CE ====
sep("14. PROTECTION RELEASE DELAY TIMES  (reg 0x00C4-0x00CE) [DOC]")
delay_fields = [
    (202, 0x00C4, "Discharge OCP release time"),
    (204, 0x00C6, "Discharge SCP release time"),
    (206, 0x00C8, "Charge OCP release time"),
    (208, 0x00CA, "Charge SCP release time"),
    (210, 0x00CC, "Cell UVP release time"),
    (212, 0x00CE, "Cell OVP release time"),
]
for off, reg, desc in delay_fields:
    val = u16(off)
    print(f"  reg 0x{reg:04X} off={off:3d}  {val:5d} s  -- {desc}")

# ==== 15. TEMPERATURE SENSOR PRESENCE [DOC] offset 214, reg 0x00D0 ====
sep("15. TEMPERATURE SENSOR PRESENCE  (offset 214, reg 0x00D0) [DOC]")
ts_byte = u8(214)
heat    = u8(215)
print(f"  Raw:          0x{ts_byte:02X}")
print(f"  BIT=1 -> sensor PRESENT (normal); BIT=0 -> sensor ABSENT")
for bit in range(6):
    present = bool(ts_byte & (1 << bit))
    label = SENSOR_PRESENCE.get(bit, f"Reserved bit {bit}")
    print(f"    BIT{bit}:  [{'PRESENT' if present else 'ABSENT '}]  {label}")
print(f"  Heating:      {'ON' if heat else 'OFF'}  (off=215, reg 0x00D1)")

# ==== 16. EMERGENCY / CURRENT CORRECTION / SENSOR VOLTAGES [DOC] offset 218-235 ====
sep("16. EMERGENCY / CURRENT CORRECTION / SENSOR VOLTAGES  (reg 0x00D4-0x00E4) [DOC]")
emerg_s  = u16(218)     # reg 0x00D4  应急开关时间 (DOC: TimeEmergency)
dis_cur  = u16(220)     # reg 0x00D6  放电电流修正因子 (DOC: VolBatCurCorrect)
chg_v    = u16(222)     # reg 0x00D8  充电电流传感器电压 (DOC: VolChargeCur)
dis_v    = u16(224)     # reg 0x00DA  放电电流传感器电压 (DOC: VolDischargeCur)
cal_f    = f32(226)     # reg 0x00DC  电池电压校准因子 (DOC: BatVolCorrect, FLOAT32)
bat_v001 = u16(234)     # reg 0x00E4  电池电压 0.01V (DOC: BatVol)
print(f"  Emergency switch time:          {emerg_s} s          (reg 0x00D4, TimeEmergency)")
print(f"  Discharge current correction:   {dis_cur}            (reg 0x00D6) [unit TBD]")
print(f"  Charge current sensor voltage:  {chg_v} mV           (reg 0x00D8)")
print(f"  Discharge current sensor V:     {dis_v} mV           (reg 0x00DA)")
print(f"  Voltage calibration factor:     {cal_f:.6f}         (reg 0x00DC, float32)")
print(f"  Battery voltage (0.01V):        {bat_v001} -> {bat_v001/100:.2f} V   (reg 0x00E4, BatVol)")

# ==== 17. HEATING / CHARGER / SYSTEM TICKS [DOC] ====
sep("17. HEATING CURRENT / CHARGER / SYSTEM UPTIME  (reg 0x00E6-0x00F0) [DOC]")
heat_ma  = s16(236)     # reg 0x00E6  HeatCurrent
charger  = u8(245)      # reg 0x00EF  ChargerPlugged
sys_ticks = u32(246)    # reg 0x00F0  SysRunTicks (0.1s unit)
print(f"  Heating current:     {heat_ma} mA = {heat_ma/1000:.3f} A  (reg 0x00E6)")
print(f"  Charger plugged:     {'YES' if charger else 'NO'}           (reg 0x00EF)")
print(f"  System run time:     {sys_ticks} ticks = {sys_ticks/10:.0f} s = {sys_ticks/10/3600:.1f} h  (reg 0x00F0, 0.1s/tick)")

# ==== 18. RTC / SLEEP / PCL / FAULT COUNT [DOC] offset 250-275 ====
sep("18. RTC TIME / SLEEP / PCL MODULE / FAULT COUNT  (reg 0x0100-0x010C) [DOC]")
rtc_raw   = u32(262)     # reg 0x0100  RTC Time
fault_cnt = u8(266)      #             FaultCount
sleep_raw = u32(270)     # reg 0x0108  TimeEnterSleep
pcl_sta   = u8(274)      # reg 0x010C  PCLModuleSta

rtc_base = datetime.datetime(2020, 1, 1)
rtc_dt = rtc_base + datetime.timedelta(seconds=rtc_raw)
print(f"  RTC time:           {rtc_raw} s  →  {rtc_dt.strftime('%Y-%m-%d %H:%M:%S')}  (reg 0x0100, since 2020-01-01)")
print(f"  Fault count:        {fault_cnt}             (off=266)")
print(f"  Enter sleep time:   {sleep_raw} s = {sleep_raw/3600:.1f} h  (reg 0x0108, TimeEnterSleep)")
print(f"  PCL module:         {'ON' if pcl_sta else 'OFF'}         (reg 0x010C, PCLModuleSta: 1=打开, 0=关闭)")

# ==== 19. TRAILING MODBUS ACK ====
sep("20. TRAILING MODBUS ACK  (bytes 300-307)")
print(f"  Raw hex:  {' '.join(f'{b:02X}' for b in ack)}")
if len(ack) == 8:
    pack_id  = ack[0]
    func     = ack[1]
    reg_addr = (ack[2] << 8) | ack[3]
    reg_cnt  = (ack[4] << 8) | ack[5]
    crc      = struct.unpack_from('<H', ack, 6)[0]
    print(f"  Byte 300 (Pack ID):      0x{pack_id:02X} ({pack_id})")
    print(f"  Byte 301 (Function):     0x{func:02X} ({'Write Multiple' if func==0x10 else 'Read Holding' if func==0x03 else '?'})")
    print(f"  Byte 302-303 (Reg addr): 0x{reg_addr:04X} ({'DYNAMIC' if reg_addr==0x1620 else 'SETUP' if reg_addr==0x161E else 'STATIC' if reg_addr==0x161C else '?'})")
    print(f"  Byte 304-305 (Count):    0x{reg_cnt:04X}")
    print(f"  Byte 306-307 (CRC):      0x{crc:04X}")
    print()
    print(f"  IMPORTANT: Byte 300 (0x{pack_id:02X}) is the Pack ID (0=pack1, 1=pack2).")
    print(f"             Byte 4 of 55AA header (0x{frame[4]:02X}) is the Frame Type.")
    print(f"             These are DIFFERENT fields!")

# ==== 21. FULL HEX DUMP OF ENTIRE FRAME ====
sep("21. FULL 300-BYTE 55AA FRAME HEX DUMP")
for row_start in range(0, 300, 16):
    row_bytes = frame[row_start:min(row_start+16, len(frame))]
    hex_str = ' '.join(f'{b:02X}' for b in row_bytes)
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row_bytes)
    print(f"  {row_start:04X}: {hex_str:48s}  {ascii_str}")

# ============================================================================
# SUMMARY
# ============================================================================
sep("SUMMARY")
print(f"  Frame Type:                    0x{frame[4]:02X} ({'DYNAMIC' if frame[4]==2 else 'SETUP' if frame[4]==1 else '?'})")
print(f"  Pack ID (in ACK):              {pack_id}")
print(f"  Frame type (from ACK reg):     0x{reg_addr:04X} (DYNAMIC)")
print(f"  Cells:                         {len(active_cells)} active")
print(f"  Cell range:                    {min(active_cells)}-{max(active_cells)} mV  (delta {max(active_cells)-min(active_cells)} mV)")
print(f"  Total voltage:                 {v_mv/1000:.3f} V")
print(f"  Current:                       {i_ma/1000:.2f} A  [{direction}]")
print(f"  Power:                         {p_mw/1000:.1f} W")
print(f"  SOC:                           {soc_val} %")
print(f"  SOH:                           {soh} %")
print(f"  MOS temp:                      {mos_t_raw/10:.1f} C")
print(f"  Balance current:               {bal_ma} mA")
print(f"  Charge MOS:                    {'ON' if chg_mos else 'OFF'}")
print(f"  Discharge MOS:                 {'ON' if dch_mos else 'OFF'}")
print(f"  Cycle count:                   {cycles}")
print(f"  Remain / Full capacity:        {remain_mah/1000:.2f} / {full_mah/1000:.2f} Ah")
print(f"  Runtime:                       {runtime} s = {runtime/3600:.1f} h")
print(f"  System run time:               {sys_ticks/10:.0f} s = {sys_ticks/10/3600:.1f} h")
print(f"  RTC time:                      {rtc_dt.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Enter sleep time:              {sleep_raw} s = {sleep_raw/3600:.1f} h")
print(f"  PCL module:                    {'ON' if pcl_sta else 'OFF'}")
print(f"  UserAlarm1 / UserAlarm2:       {user_al1} / {user_al2}")
print(f"  Alarm bitfield:                0x{alarm_raw:08X}")
print(f"  Active alarm count:            {len(active_alarms)}")
if active_alarms:
    for bit, en, cn in active_alarms:
        print(f"    - BIT{bit}: {en} ({cn})")
print(f"  All temp sensors:              {'ALL PRESENT' if ts_byte == 0xFF else f'0x{ts_byte:02X}'}")
print(f"  Charger plugged:               {'YES' if charger else 'NO'}")
print(f"  Heating:                       {'ON' if heat else 'OFF'}")
print()
print("  Legend: [VERIFIED] = offset confirmed by working parser")
print("          [DOC]       = offset from protocol document (frame = reg + 6)")
print("                        May be incorrect if 55AA layout differs from register map")
