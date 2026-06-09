#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import logging
import threading
import time

class JKBMS485:
    """
    JK BMS RS485 Communication Class
    Implements JK BMS RS485 protocol (passive listening mode).

    Protocol summary:
    - The JK BMS automatically broadcasts data frames without needing any query commands.
    - 55AA frames (308 bytes) contain battery data: cell voltages, current, SOC, temps.
    - The BMS broadcasts every ~200ms — this class passively listens and parses.
    - If no battery data is available, short 11-byte Modbus ACK frames are received instead.
    - No commands are sent; the BMS acts as a continuous broadcaster.

    Frame offsets calibrated for firmware 9.04 (JK_PB1A16S10P, 16S LFP).
    Other firmware versions may have different 55AA frame layouts.
    """

    def __init__(self, bms_comm, ha_comm, bms_type, data_refresh_interval, debug, if_random, ha_comm_jk=None, pack_index_start=1):
        self.bms_comm = bms_comm
        self.ha_comm = ha_comm
        self.ha_comm_jk = ha_comm_jk          # JK-native MQTT publisher (HA_MQTT_JK or None)
        self.bms_type = bms_type
        self.data_refresh_interval = data_refresh_interval
        self.debug = debug
        self.if_random = if_random
        self.pack_index_start = pack_index_start


        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # JK BMS register addresses used for frame identification in passive listening
        self.REG_STATIC = 0x161C    # Trame 1 - Static data (version, serial, etc.)
        self.REG_SETUP  = 0x161E    # Trame 2 - Setup/Config data
        self.REG_DYNAMIC = 0x1620   # Trame 3 - Dynamic data (cells, current, SOC, etc.)
        # Cumulative energy tracking
        self.pack_energy = {}  # dict of pack_id -> {'charged': 0.0, 'discharged': 0.0, 'last_time': float}
        # Setup and Static data caching (infrequently broadcasted frames)
        self.setup_cache = {}   # dict of pack_id -> setup_dict
        self.static_cache = {}  # dict of pack_id -> static_dict
        # Cache of dynamic frames to avoid pack count/data fluctuations
        self.dynamic_cache = {} # dict of pack_id -> (dynamic_dict, timestamp)
        
        # Thread safety lock and background listener thread
        self.cache_lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, name="jkbms_listener", daemon=True)
        self.thread.start()

    # ---------------------------------------------------------------------------
    # Cumulative Energy
    # ---------------------------------------------------------------------------
    def calculate_cumulative_energy(self, pack_id, power_kw):
        """
        Calculate cumulative energy (Wh) per pack based on power and time delta.
        """
        import time
        current_time = time.time()
        
        if pack_id not in self.pack_energy:
            self.pack_energy[pack_id] = {'charged': 0.0, 'discharged': 0.0, 'last_time': current_time}
            return 0.0, 0.0
            
        pack_data = self.pack_energy[pack_id]
        time_diff = current_time - pack_data['last_time']
        
        # Abnormal interval detection (>5 mins)
        if time_diff > 300:
            self.logger.warning(f"Abnormal time interval for pack {pack_id}: {time_diff:.1f}s, resetting time base")
            pack_data['last_time'] = current_time
            return pack_data['charged'], pack_data['discharged']
            
        # Ignore very short intervals (<1s)
        if time_diff < 1:
            return pack_data['charged'], pack_data['discharged']
            
        # kW to W, seconds to hours -> Wh
        energy_increment = abs(power_kw) * time_diff / 3600 * 1000
        
        if power_kw >= 0:
            pack_data['charged'] += energy_increment
        else:
            pack_data['discharged'] += energy_increment
            
        pack_data['last_time'] = current_time
        return pack_data['charged'], pack_data['discharged']

    # ---------------------------------------------------------------------------
    # CRC16 Modbus
    # ---------------------------------------------------------------------------
    def calculate_crc16_modbus(self, data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    # ---------------------------------------------------------------------------
    # Passive data reception (BMS broadcasts 55AA frames automatically)
    # ---------------------------------------------------------------------------

    def stop(self):
        """Stop the background listener thread."""
        self.running = False

    def _validate_ack_at(self, buffer, offset):
        """Check if a valid Modbus ACK exists at the given offset.
        ACK format: [pack_id][0x10][reg_hi][reg_lo][0x00][0x01][crc16_le]
        Returns (True, reg_addr, pack_id) or (False, 0, 0)."""
        if offset + 8 > len(buffer):
            return False, 0, 0
        ack = buffer[offset:offset + 8]
        if ack[1] != 0x10:
            return False, 0, 0
        if ack[4] != 0x00 or ack[5] != 0x01:
            return False, 0, 0
        crc_expected = self.calculate_crc16_modbus(ack[0:6])
        crc_received = struct.unpack('<H', ack[6:8])[0]
        if crc_expected != crc_received:
            return False, 0, 0
        reg_addr = (ack[2] << 8) | ack[3]
        pack_id = ack[0]
        return True, reg_addr, pack_id

    def _handle_valid_frame(self, frame, reg_addr, pack_id):
        """Thread-safely parse and update cache dicts."""
        current_time = time.time()
        reg_label = (
            'DYNAMIC' if reg_addr == 0x1620
            else 'SETUP' if reg_addr == 0x161E
            else 'STATIC' if reg_addr == 0x161C
            else 'UNKNOWN')
            
        self.logger.debug(
            f"Background parsed valid frame: pack_id={pack_id}, reg=0x{reg_addr:04X} ({reg_label})"
        )
        
        with self.cache_lock:
            if reg_addr == 0x1620:
                res = self.parse_jkbms_55aa_frame(frame)
                if res.get('cell_voltages'):
                    self.dynamic_cache[pack_id] = (res, current_time)
            elif reg_addr == 0x161E:
                res = self.parse_jkbms_setup_frame(frame)
                if res:
                    self.setup_cache[pack_id] = res
            elif reg_addr == 0x161C:
                res = self.parse_jkbms_static_frame(frame)
                if res:
                    self.static_cache[pack_id] = res

    def _read_loop(self):
        """
        Background listener thread loop.
        Passively reads from the BMS connection,
        accumulates bytes, parses 55AA frames, and updates caches.
        """
        self.logger.info("JK BMS background listener thread started")
        buffer = b''
        while self.running:
            try:
                # Read raw passive data
                raw_data = self.bms_comm.receive_jkbms_passive(read_timeout=1.0)
                if raw_data:
                    # Append new data to sliding buffer
                    buffer += raw_data
                    
                    # Process buffer
                    while len(buffer) >= 8:
                        # 1. Find the first occurrence of 55 AA
                        idx = buffer.find(b'\x55\xAA')
                        if idx < 0:
                            # 55 AA not found, discard everything except the last 1 byte (in case it is 0x55)
                            if buffer.endswith(b'\x55'):
                                buffer = b'\x55'
                            else:
                                buffer = b''
                            break
                        
                        if idx > 0:
                            # Discard non-55AA data preceding the match
                            buffer = buffer[idx:]
                        
                        # 2. Check if we have enough bytes to scan for ACK
                        # Max possible offset to check is 340, ACK size is 8.
                        # We need at least 348 bytes to do a full scan.
                        if len(buffer) < 348:
                            # Wait for more data to complete the frame
                            break
                            
                        matched = False
                        for offset in range(280, 341):
                            valid, reg_addr, pack_id = self._validate_ack_at(buffer, offset)
                            if valid and reg_addr in {0x161C, 0x161E, 0x1620}:
                                frame = buffer[:300]
                                self._handle_valid_frame(frame, reg_addr, pack_id)
                                buffer = buffer[offset + 8:]
                                matched = True
                                break
                                
                        if not matched:
                            # Checked 280 to 340 and found no valid ACK. Invalid header!
                            # Discard first 2 bytes (55 AA) to search for the next 55 AA.
                            buffer = buffer[2:]
                else:
                    # No data received, sleep a bit to prevent high CPU usage
                    time.sleep(0.05)
            except Exception as e:
                self.logger.error(f"Error in background listener thread: {e}", exc_info=True)
                time.sleep(1.0)
                
        self.logger.info("JK BMS background listener thread stopped")

    # ---------------------------------------------------------------------------
    # 55AA JK BMS Frame Parser
    # ---------------------------------------------------------------------------
    # Frame offsets match reference documentation (jkbms-rs485-addon).
    # Verified against firmware 9.04 (JK_PB1A16S10P, 16S LFP) via live captures.
    #
    # Reference offsets (from RS485-Frames-decoded.md + live verification):
    #   Cell voltages:      uint16le at 6   (×16, mV)
    #   Cell resistance:    int16le  at 80  (×16, mΩ)
    #   MOS temp:           int16le  at 144 (/10 = °C)
    #   Voltage (mV):       uint32le at 150 (mV)
    #   Power:              uint32le at 154 (mW)
    #   Current:            int32le  at 158 (mA)
    #   Temp sensor 1:      int16le  at 162 (/10 = °C)
    #   Temp sensor 2:      int16le  at 164 (/10 = °C)
    #   Balance current:    int16le  at 170 (mA)
    #   Balance action:     uint8    at 172
    #   SOC:                uint8    at 173 (%)
    #   Remain capacity:    uint32le at 174 (mAh, /1000 = Ah)
    #   Full capacity:      uint32le at 178 (mAh, /1000 = Ah)
    #   Cycle count:        uint32le at 182
    #   Cycle capacity:     uint32le at 186 (mAh, /1000 = Ah)
    #   SOH:                uint8    at 190 (%)
    #   Total runtime:      uint32le at 194 (s)
    #   Charge MOS:         uint8    at 198
    #   Discharge MOS:      uint8    at 199
    #   Balance MOS:        uint8    at 200
    #   Total voltage:      uint16le at 234 (/100 = V)
    #   Temp sensor 3:      int16le  at 254 (/10 = °C)
    #   Temp sensor 4:      int16le  at 258 (/10 = °C)
    #   Fault record count: uint8    at 266
    # ---------------------------------------------------------------------------

    def parse_jkbms_55aa_frame(self, data):
        """
        Parse a JK BMS proprietary 55AA data frame.

        Offsets match the reference documentation (RS485-Frames-decoded.md)
        and verified against firmware 9.04 (JK_PB1A16S10P, 16S LFP).

        Returns dict with parsed values or empty dict on failure.
        """
        result = {}

        if not data or len(data) < 6 or data[0] != 0x55 or data[1] != 0xAA:
            self.logger.warning(f"Not a valid 55AA frame (len={len(data) if data else 0})")
            return result

        self.logger.debug(f"Parsing 55AA frame, {len(data)} bytes")

        # ---- Cell voltages: uint16le at offset 6 (16 cells, mV) ----
        cells = []
        for i in range(16):
            offset = 6 + i * 2
            if offset + 1 < len(data):
                raw_mv = struct.unpack_from('<H', data, offset)[0]
                if raw_mv > 0 and raw_mv < 50000:
                    cells.append(raw_mv)
                else:
                    break
            else:
                break
        if cells:
            result['cell_voltages'] = cells

        # ---- Cell resistance: int16le at offset 80 (16 cells, mΩ) ----
        cell_resistances = []
        for i in range(16):
            offset = 80 + i * 2
            if offset + 1 < len(data):
                raw_mohm = struct.unpack_from('<h', data, offset)[0]
                if 0 <= raw_mohm <= 1000:
                    cell_resistances.append(raw_mohm)
                else:
                    break
            else:
                break
        if cell_resistances:
            result['cell_resistances'] = cell_resistances

        # ---- Cell exist state: uint32le at offset 70 ----
        if 74 <= len(data):
            result['cell_exist_state'] = struct.unpack_from('<I', data, 70)[0]

        # ---- Voltage stats: avg (74-75), diff (76-77), max_idx (78), min_idx (79) ----
        if 80 <= len(data):
            result['cell_voltage_avg'] = struct.unpack_from('<H', data, 74)[0]
            result['cell_voltage_diff'] = struct.unpack_from('<H', data, 76)[0]
            result['cell_voltage_max_index'] = int(data[78])
            result['cell_voltage_min_index'] = int(data[79])

        # ---- MOS temp: int16le at offset 144 (/10 = °C) ----
        if 146 <= len(data):
            raw_mos = struct.unpack_from('<h', data, 144)[0]
            if -500 < raw_mos < 1500:
                result['temp_mos'] = raw_mos / 10.0

        # ---- Wire alarms: uint32le at offset 146 ----
        if 150 <= len(data):
            result['wire_alarm'] = struct.unpack_from('<I', data, 146)[0]

        # ---- Total voltage (high precision): uint32le at offset 150 (mV) ----
        if 154 <= len(data):
            raw_v = struct.unpack_from('<I', data, 150)[0]
            if raw_v > 0:
                result['voltage_v'] = raw_v / 1000.0

        # ---- Power: uint32le at offset 154 (mW) ----
        if 158 <= len(data):
            raw_p = struct.unpack_from('<I', data, 154)[0]
            result['power_kw'] = raw_p / 1000000.0  # mW → kW

        # ---- Current: int32le at offset 158 (mA) ----
        if 162 <= len(data):
            raw_c = struct.unpack_from('<i', data, 158)[0]
            result['current_a'] = raw_c / 1000.0  # mA → A

        # ---- Battery temp sensors: int16le at 162, 164, 254, 256, 258 (/10 = °C) ----
        temps = {
            'temp_bat1': 162,
            'temp_bat2': 164,
            'temp_bat3': 254,
            'temp_bat4': 256,
            'temp_bat5': 258,
        }
        for name, off in temps.items():
            if off + 2 <= len(data):
                raw = struct.unpack_from('<h', data, off)[0]
                if -500 < raw < 1500:
                    result[name] = raw / 10.0

        # ---- Balance current: int16le at offset 170 (mA) ----
        if 172 <= len(data):
            raw_bal = struct.unpack_from('<h', data, 170)[0]
            if -10000 < raw_bal < 10000:
                result['balance_current_a'] = raw_bal / 1000.0  # mA → A

        # ---- Alarm bits: uint32le at offset 166 ----
        if 170 <= len(data):
            result['alarm_bits'] = struct.unpack_from('<I', data, 166)[0]

        # ---- Battery state: uint8 at 172 ----
        if 173 <= len(data):
            result['battery_state'] = int(data[172])

        # ---- SOC: uint8 at offset 173 (%) ----
        if 174 <= len(data):
            soc_val = data[173]
            if 0 <= soc_val <= 100:
                result['soc'] = float(soc_val)

        # ---- Capacity: uint32le at 174 (remain mAh) and 178 (full mAh) ----
        if 182 <= len(data):
            remain = struct.unpack_from('<I', data, 174)[0]
            if 0 < remain <= 5000000000:
                result['remain_capacity_ah'] = remain / 1000.0
        if 182 <= len(data):
            full = struct.unpack_from('<I', data, 178)[0]
            if 0 < full <= 5000000000:
                result['full_capacity_ah'] = full / 1000.0

        # ---- Cycle count: uint32le at offset 182 ----
        if 186 <= len(data):
            cc = struct.unpack_from('<I', data, 182)[0]
            if 0 <= cc < 65000:
                result['cycle_count'] = cc

        # ---- Cycle capacity: uint32le at offset 186 (mAh) ----
        if 190 <= len(data):
            cycle_cap = struct.unpack_from('<I', data, 186)[0]
            result['cycle_capacity_ah'] = cycle_cap / 1000.0

        # ---- SOH: uint8 at offset 190 (%) ----
        if 190 < len(data):
            soh = data[190]
            if 0 < soh <= 100:
                result['soh'] = float(soh)

        # ---- Precharge state: uint8 at 191 ----
        if 192 <= len(data):
            result['precharge_state'] = int(data[191])

        # ---- User Alarm 1: uint16le at 192 ----
        if 194 <= len(data):
            result['user_alarm_1'] = struct.unpack_from('<H', data, 192)[0]

        # ---- Total runtime: uint32le at offset 194 (s) ----
        if 198 <= len(data):
            runtime = struct.unpack_from('<I', data, 194)[0]
            result['total_runtime_s'] = runtime

        # ---- MOS status: uint8 at 198 (charge), 199 (discharge), 200 (balance) ----
        if 201 < len(data):
            result['charge_mos'] = bool(data[198])
            result['discharge_mos'] = bool(data[199])
            result['balance_mos'] = bool(data[200])

        # ---- Protect release delays (202-213) ----
        if 214 <= len(data):
            result['time_de_ocpr'] = struct.unpack_from('<H', data, 202)[0]
            result['time_de_scpr'] = struct.unpack_from('<H', data, 204)[0]
            result['time_ch_ocpr'] = struct.unpack_from('<H', data, 206)[0]
            result['time_ch_uvpr'] = struct.unpack_from('<H', data, 208)[0]
            result['time_uvpr'] = struct.unpack_from('<H', data, 210)[0]
            result['time_ovpr'] = struct.unpack_from('<H', data, 212)[0]

        # ---- Temp sensor presence (214), Heating state (215) ----
        if 216 <= len(data):
            result['temp_sensor_presence'] = int(data[214])
            result['heating_state'] = int(data[215])

        # ---- Emergency switch time (218-219) ----
        if 220 <= len(data):
            result['time_emergency'] = struct.unpack_from('<H', data, 218)[0]

        # ---- Correct factor / sensor voltage (220-229) ----
        if 230 <= len(data):
            result['vol_bat_cur_correct'] = struct.unpack_from('<H', data, 220)[0]
            result['vol_charge_cur'] = struct.unpack_from('<H', data, 222)[0]
            result['vol_discharge_cur'] = struct.unpack_from('<H', data, 224)[0]
            result['bat_vol_correct'] = struct.unpack_from('<f', data, 226)[0]

        # ---- Total voltage (standard precision): uint16le at 234 (/100 = V) ----
        if 236 <= len(data):
            raw_sv = struct.unpack_from('<H', data, 234)[0]
            if raw_sv > 0:
                if 'voltage_v' not in result:
                    result['voltage_v'] = raw_sv / 100.0

        # ---- HeatCurrent (236-237) ----
        if 238 <= len(data):
            result['heat_current_a'] = struct.unpack_from('<h', data, 236)[0] / 1000.0

        # ---- Charger plugged (245) ----
        if 246 <= len(data):
            result['charger_plugged'] = int(data[245])

        # ---- SysRunTicks (246-249) ----
        if 250 <= len(data):
            result['sys_run_ticks'] = struct.unpack_from('<I', data, 246)[0]

        # ---- RTC Time (262-265) ----
        if 266 <= len(data):
            result['rtc_time'] = struct.unpack_from('<I', data, 262)[0]

        # ---- Fault record count: uint8 at offset 266 ----
        if 267 <= len(data):
            result['fault_count'] = int(data[266])

        # ---- TimeEnterSleep (270-273) ----
        if 274 <= len(data):
            result['time_enter_sleep'] = struct.unpack_from('<I', data, 270)[0]

        # ---- PCLModuleSta (274) ----
        if 275 <= len(data):
            result['pcl_module_sta'] = int(data[274])

        self.logger.debug(f"Parsed 55AA frame: {result}")
        return result

    def dump_frame_analysis(self, data):
        """
        Diagnostic tool: dump a 55AA frame with all potential field locations.
        Use this when calibrating offsets for a new BMS firmware version.

        Call this with raw response data after receiving to see annotated hex dump
        with interpretations of every word in the frame.
        """
        if not data or len(data) < 6 or data[0] != 0x55 or data[1] != 0xAA:
            self.logger.warning("Not a valid 55AA frame for analysis")
            return

        print("=" * 70)
        print("JK BMS 55AA FRAME ANALYSIS")
        print("=" * 70)
        print(f"Frame length: {len(data)} bytes")
        print(f"Pack ID:      {data[4]} (offset 4)")
        print()

        # Print hex dump with interpretations
        for row_start in range(0, len(data), 16):
            row_end = min(row_start + 16, len(data))
            row_data = data[row_start:row_end]

            hex_part = ' '.join(f'{b:02X}' for b in row_data)
            hex_padded = hex_part.ljust(48)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row_data)

            notes = []
            for i, b in enumerate(row_data):
                abs_offset = row_start + i

                if abs_offset == 0:
                    notes.append("← 55AA Header")
                if abs_offset == 144:
                    if abs_offset + 1 < len(data):
                        t = struct.unpack_from('<h', data, 144)[0] / 10.0
                        notes.append(f"← MOS temp={t:.1f}°C")
                if abs_offset == 150:
                    if abs_offset + 3 < len(data):
                        v = struct.unpack_from('<I', data, 150)[0] / 1000.0
                        notes.append(f"← V={v:.3f}V(uint32 mV)")
                if abs_offset == 154:
                    notes.append("← Power(uint32 mW)")
                if abs_offset == 158:
                    notes.append("← Current(int32 mA)")
                if abs_offset == 162:
                    notes.append("← Temp1(int16/10)")
                if abs_offset == 164:
                    notes.append("← Temp2(int16/10)")
                if abs_offset == 170:
                    notes.append("← Balance A")
                if abs_offset == 173:
                    notes.append(f"← SOC={data[173]}%")
                if abs_offset == 174:
                    if abs_offset + 3 < len(data):
                        cap = struct.unpack_from('<I', data, 174)[0] / 1000.0
                        notes.append(f"← Remain={cap:.1f}Ah")
                if abs_offset == 178:
                    if abs_offset + 3 < len(data):
                        cap = struct.unpack_from('<I', data, 178)[0] / 1000.0
                        notes.append(f"← FullCap={cap:.1f}Ah")
                if abs_offset == 182:
                    notes.append("← Cycles")
                if abs_offset == 190:
                    notes.append(f"← SOH={data[190]}%")
                if abs_offset == 198:
                    notes.append("← ChgMOS")
                if abs_offset == 199:
                    notes.append("← DchMOS")
                if abs_offset == 234:
                    if abs_offset + 1 < len(data):
                        v = struct.unpack_from('<H', data, 234)[0] / 100.0
                        notes.append(f"← V={v:.2f}V(uint16)")

                # Cell voltages (offset 6-37)
                if 6 <= abs_offset <= 37 and (abs_offset - 6) % 2 == 0:
                    if abs_offset + 1 < len(data):
                        mv = struct.unpack_from('<H', data, abs_offset)[0]
                        if 2000 <= mv <= 5000:
                            cell_num = (abs_offset - 6) // 2 + 1
                            notes.append(f"← C{cell_num}={mv}mV")

                # Cell resistance (offset 80-111)
                if 80 <= abs_offset <= 110 and (abs_offset - 80) % 2 == 0:
                    if abs_offset + 1 < len(data):
                        r = struct.unpack_from('<h', data, abs_offset)[0]
                        if 0 <= r <= 1000:
                            cell_num = (abs_offset - 80) // 2 + 1
                            notes.append(f"← R{cell_num}={r}mΩ")

            note_str = '; '.join(notes) if notes else ''
            if note_str:
                print(f"  {row_start:04X}: {hex_padded} |{ascii_part}| {note_str}")
            else:
                print(f"  {row_start:04X}: {hex_padded} |{ascii_part}|")

        # Scan section
        print()
        print("--- FIELD SCAN ---")
        print()

        # Temperatures
        print("Temperature candidates (int16le/10, -10 to 100°C):")
        for off in range(0, len(data) - 1):
            if off % 2 != 0:
                continue
            raw = struct.unpack_from('<h', data, off)[0]
            if -100 < raw < 1000:
                print(f"  offset {off:3d} (0x{off:04X}): {raw/10:.1f}°C")

        # Voltage
        cell_mvs = [struct.unpack_from('<H', data, 6+i*2)[0] for i in range(16)
                    if 6+i*2+1 < len(data) and 2000 <= struct.unpack_from('<H', data, 6+i*2)[0] <= 5000]
        total_mv = sum(cell_mvs) if cell_mvs else 0

        print()
        print("Voltage candidates (uint16le mV):")
        for off in range(len(data) - 1):
            raw = struct.unpack_from('<H', data, off)[0]
            if 10000 < raw < 60000:
                mark = " ← MATCH" if total_mv and abs(raw - total_mv) < 500 else ""
                print(f"  offset {off:3d}: {raw}mV = {raw/1000:.3f}V{mark}")

        print()
        print("Voltage candidates (uint32le mV):")
        for off in range(len(data) - 3):
            raw = struct.unpack_from('<I', data, off)[0]
            if 10000 < raw < 60000:
                mark = " ← MATCH" if total_mv and abs(raw - total_mv) < 500 else ""
                print(f"  offset {off:3d}: {raw}mV = {raw/1000:.3f}V{mark}")

        print()
        print("Current candidates (int32le mA):")
        for off in range(len(data) - 3):
            raw = struct.unpack_from('<i', data, off)[0]
            if -500000 < raw < 500000 and (abs(raw) > 1000 or raw == 0):
                label = " ← ZERO" if raw == 0 else ""
                print(f"  offset {off:3d}: {raw}mA = {raw/1000:.2f}A{label}")

        print()
        print("Power candidates (uint32le mW):")
        for off in range(len(data) - 3):
            raw = struct.unpack_from('<I', data, off)[0]
            if 1000 < raw < 50000000:
                print(f"  offset {off:3d}: {raw}mW = {raw/1000:.1f}W = {raw/1000000:.3f}kW")

        print()
        print("Capacity candidates (uint32le mAh):")
        for off in range(len(data) - 3):
            raw = struct.unpack_from('<I', data, off)[0]
            if 90000 < raw < 110000:
                print(f"  offset {off:3d}: {raw/1000:.3f}Ah")

        print()
        print("--- END FRAME ANALYSIS ---")
        print("=" * 70)

    def parse_jkbms_static_frame(self, data):
        """
        Parse JK BMS static data 55AA frame (from register 0x161C).
        Extracts hardware/software version info.

        Based on reference buffer-parser Trame 1 layout.
        """
        result = {}
        if not data or len(data) < 6 or data[0] != 0x55 or data[1] != 0xAA:
            return result

        # BMS name: ASCII at offset 6, 13 chars
        if len(data) >= 19:
            bms_name = data[6:19].decode('ascii', errors='ignore').rstrip('\x00').strip()
            if bms_name:
                result['bms_name'] = bms_name

        # Hardware version (FW_A): ASCII at offset 22, 3 chars
        if len(data) >= 25:
            hw_ver = data[22:25].decode('ascii', errors='ignore').rstrip('\x00').strip()
            if hw_ver:
                result['hardware_version'] = hw_ver

        # Software version (SW_N): ASCII at offset 30, 5 chars
        if len(data) >= 35:
            sw_ver = data[30:35].decode('ascii', errors='ignore').rstrip('\x00').strip()
            if sw_ver:
                result['software_version'] = sw_ver

        # Serial number: ASCII at offset 46, 13 chars
        if len(data) >= 59:
            serial = data[46:59].decode('ascii', errors='ignore').rstrip('\x00').strip()
            if serial:
                result['serial_number'] = serial

        # Manufacturing date: ASCII at offset 78, 8 chars
        if len(data) >= 86:
            mfg_date = data[78:86].decode('ascii', errors='ignore').rstrip('\x00').strip()
            if mfg_date:
                result['manufacturing_date'] = mfg_date

        self.logger.debug(f"Parsed static frame: {result}")
        return result

    def parse_jkbms_setup_frame(self, data):
        """
        Parse JK BMS setup data 55AA frame (from register 0x161E).
        """
        result = {}
        if not data or len(data) < 6 or data[0] != 0x55 or data[1] != 0xAA:
            return result

        if 50 <= len(data):
            result['vol_smart_sleep'] = struct.unpack_from('<I', data, 6)[0] / 1000.0
            result['vol_cell_uvp'] = struct.unpack_from('<I', data, 10)[0] / 1000.0
            result['vol_cell_uvpr'] = struct.unpack_from('<I', data, 14)[0] / 1000.0
            result['vol_cell_ovp'] = struct.unpack_from('<I', data, 18)[0] / 1000.0
            result['vol_cell_ovpr'] = struct.unpack_from('<I', data, 22)[0] / 1000.0
            result['vol_balan_trig'] = struct.unpack_from('<I', data, 26)[0] / 1000.0
            result['vol_soc_100'] = struct.unpack_from('<I', data, 30)[0] / 1000.0
            result['vol_soc_0'] = struct.unpack_from('<I', data, 34)[0] / 1000.0
            result['vol_bat_uvp'] = struct.unpack_from('<I', data, 38)[0] / 1000.0
            result['vol_bat_ovp'] = struct.unpack_from('<I', data, 42)[0] / 1000.0
            result['vol_sys_pwr_off'] = struct.unpack_from('<I', data, 46)[0] / 1000.0

        if 82 <= len(data):
            result['cur_bat_c_oc'] = struct.unpack_from('<i', data, 50)[0] / 1000.0
            result['tim_bat_c_ocp_dly'] = struct.unpack_from('<I', data, 54)[0]
            result['tim_bat_c_ocpr_dly'] = struct.unpack_from('<I', data, 58)[0]
            result['cur_bat_dc_oc'] = struct.unpack_from('<I', data, 62)[0] / 1000.0
            result['tim_bat_dc_ocp_dly'] = struct.unpack_from('<I', data, 66)[0]
            result['tim_bat_dc_ocpr_dly'] = struct.unpack_from('<I', data, 70)[0]
            result['tim_bat_scpr_dly'] = struct.unpack_from('<I', data, 74)[0]
            result['cur_balan_max'] = struct.unpack_from('<I', data, 78)[0] / 1000.0

        if 114 <= len(data):
            result['tmp_bat_cot'] = struct.unpack_from('<i', data, 82)[0] / 10.0
            result['tmp_bat_cotpr'] = struct.unpack_from('<i', data, 86)[0] / 10.0
            result['tmp_bat_dot'] = struct.unpack_from('<i', data, 90)[0] / 10.0
            result['tmp_bat_dotpr'] = struct.unpack_from('<i', data, 94)[0] / 10.0
            result['tmp_bat_cut'] = struct.unpack_from('<i', data, 98)[0] / 10.0
            result['tmp_bat_cutpr'] = struct.unpack_from('<i', data, 102)[0] / 10.0
            result['tmp_mos_otp'] = struct.unpack_from('<i', data, 106)[0] / 10.0
            result['tmp_mos_otpr'] = struct.unpack_from('<i', data, 110)[0] / 10.0

        if 138 <= len(data):
            result['cell_count'] = struct.unpack_from('<I', data, 114)[0]
            result['bat_charge_en'] = struct.unpack_from('<I', data, 118)[0]
            result['bat_discharge_en'] = struct.unpack_from('<I', data, 122)[0]
            result['balan_en'] = struct.unpack_from('<I', data, 126)[0]
            result['cap_bat_cell'] = struct.unpack_from('<I', data, 130)[0] / 1000.0
            result['scp_delay'] = struct.unpack_from('<I', data, 134)[0]

        if 142 <= len(data):
            result['vol_start_balan'] = struct.unpack_from('<I', data, 138)[0] / 1000.0

        if 270 <= len(data):
            calibs = []
            for i in range(32):
                calibs.append(struct.unpack_from('<i', data, 142 + i*4)[0])
            result['wire_res_calib'] = calibs

        if 287 <= len(data):
            result['dev_addr'] = struct.unpack_from('<I', data, 270)[0]
            result['tim_precharge'] = struct.unpack_from('<I', data, 274)[0]
            result['func_bit_field'] = struct.unpack_from('<H', data, 282)[0]
            result['tim_smart_sleep'] = int(data[286])

        self.logger.debug(f"Parsed setup frame: {result}")
        return result

    def _decode_alarms(self, alarm_value):
        """Decode 32-bit alarm bitfield into structured dict."""
        alarm_bits = {
            0: "Battery SCP",
            1: "MOS over-temperature protection",
            2: "Cell qty mismatch",
            3: "Cell OVP",
            4: "Cell UVP",
            5: "Battery OVP",
            6: "Battery UVP",
            7: "Charge OCP",
            8: "Discharge OCP",
            9: "Charge over-temperature",
            10: "Aux CPU comm fault",
            11: "Cell UVP (2nd)",
            12: "Battery OVP (2nd)",
            13: "Battery UVP (2nd)",
            14: "Charge OCP (2nd)",
            15: "Discharge OCP (2nd)",
            16: "Charge low-temperature protection",
            17: "Discharge over-temperature",
            18: "GPS disconnected",
            19: "Password modify reminder",
            20: "Discharge activate failure",
            21: "Bat temp sensor anomaly",
            22: "Temperature sensor anomaly",
            23: "Parallel module fault",
        }

        active = {}
        for bit, desc in alarm_bits.items():
            active[desc] = bool(alarm_value & (1 << bit))

        return {
            'raw_value': alarm_value,
            'active_count': bin(alarm_value).count('1') & 0xFF,
            'has_alarms': alarm_value != 0,
            'alarms': active,
        }

    # ---------------------------------------------------------------------------
    # Data retrieval methods
    # ---------------------------------------------------------------------------
    def get_all_frames_data(self, force_refresh=False):
        """
        Fetch all available 55AA frames (Dynamic, Setup, Static) from passively received broadcast.
        Returns three dictionaries: dynamic_results, setup_results, static_results.
        """
        import time
        current_time = time.time()

        # Wait up to 10 seconds at startup (if caches are empty) to let background thread populate data
        start_wait = current_time
        while not self.dynamic_cache and (time.time() - start_wait < 10.0):
            time.sleep(0.2)

        dynamic_results = {}
        setup_results = {}
        static_results = {}

        # Acquire lock and copy/update from cache
        with self.cache_lock:
            # Merge cached dynamic values for packs that have been seen recently
            max_age = max(30.0, self.data_refresh_interval * 3.0)
            for p_id, (cached_res, last_seen) in list(self.dynamic_cache.items()):
                if current_time - last_seen <= max_age:
                    dynamic_results[p_id] = cached_res.copy()
                else:
                    # Clean up expired cache
                    self.logger.warning(f"Pack {p_id} went offline (no data for {max_age}s), removing from cache")
                    self.dynamic_cache.pop(p_id, None)
                    self.setup_cache.pop(p_id, None)
                    self.static_cache.pop(p_id, None)

            # Copy setup and static caches
            for p_id, setup_data in self.setup_cache.items():
                if p_id in dynamic_results:
                    setup_results[p_id] = setup_data.copy()
            for p_id, static_data in self.static_cache.items():
                if p_id in dynamic_results:
                    static_results[p_id] = static_data.copy()

        return dynamic_results, setup_results, static_results

    # ---------------------------------------------------------------------------
    # Main data gathering (compatible interface with original code)
    # ---------------------------------------------------------------------------
    def get_analog_data(self, pack_number=None):
        """
        Get all analog data from JK BMS.
        Returns list of pack dicts compatible with PACE BMS format.
        """
        self.logger.debug("Starting to get JK BMS analog data")

        dynamic_results, setup_results, static_results = self.get_all_frames_data()
        if not dynamic_results:
            self.logger.warning("Failed to get dynamic data, retrying once...")
            import time
            time.sleep(0.5)
            dyn2, set2, stat2 = self.get_all_frames_data()
            dynamic_results.update(dyn2)
            setup_results.update(set2)
            static_results.update(stat2)
            if not dynamic_results:
                self.logger.error("Failed to get dynamic data after retry")
                return []

        pack_list = []
        for pack_id, dynamic in dynamic_results.items():
            static = static_results.get(pack_id) if static_results else None
            setup = setup_results.get(pack_id) if setup_results else None
            pack_data = {}
            pack_data['pack_id'] = pack_id

            # Cell voltages
            cells = dynamic.get('cell_voltages', [])
            pack_data['cell_voltages'] = cells
            pack_data['view_num_cells'] = len(cells)
            if cells:
                # pacebms 命名格式: cell_voltage_max, cell_voltage_min
                pack_data['cell_voltage_max'] = max(cells)
                pack_data['cell_voltage_min'] = min(cells)
                # pacebms 使用 1-based index，协议提取的是 0-based
                pack_data['cell_voltage_max_index'] = dynamic.get('cell_voltage_max_index', cells.index(max(cells))) + 1
                pack_data['cell_voltage_min_index'] = dynamic.get('cell_voltage_min_index', cells.index(min(cells))) + 1
                pack_data['cell_voltage_diff'] = dynamic.get('cell_voltage_diff', max(cells) - min(cells))
                
                if 'cell_voltage_avg' in dynamic:
                    pack_data['cell_voltage_avg'] = dynamic['cell_voltage_avg']
            else:
                pack_data['cell_voltage_max'] = 0
                pack_data['cell_voltage_min'] = 0
                pack_data['cell_voltage_max_index'] = 0
                pack_data['cell_voltage_min_index'] = 0
                pack_data['cell_voltage_diff'] = 0

            # Cell resistances
            if 'cell_resistances' in dynamic:
                pack_data['cell_resistances'] = dynamic['cell_resistances']

            # Temperatures (Protocol specifies Bat1-5 and MOS)
            temps = []
            for key in ['temp_bat1', 'temp_bat2', 'temp_bat3', 'temp_bat4', 'temp_bat5', 'temp_mos']:
                val = dynamic.get(key)
                if val is not None and -50 <= val <= 150:
                    temps.append(round(val, 1))
            pack_data['temperatures'] = temps
            pack_data['view_num_temps'] = len(temps)

            # Current, Voltage, Power
            pack_data['view_current'] = dynamic.get('current_a', 0.0)
            pack_data['view_voltage'] = dynamic.get('voltage_v', 0.0)
            pack_data['view_power'] = dynamic.get('power_kw', 0.0)

            # Balance current
            if 'balance_current_a' in dynamic:
                pack_data['view_balance_current'] = dynamic['balance_current_a']

            # SOC & capacity
            pack_data['view_SOC'] = dynamic.get('soc', 0.0)
            pack_data['view_remain_capacity'] = dynamic.get('remain_capacity_ah', 0.0)
            pack_data['view_full_capacity'] = dynamic.get('full_capacity_ah', 0.0)
            # view_design_capacity 不在 DYNAMIC 帧协议内，取消发送
            
            pack_data['view_cycle_number'] = dynamic.get('cycle_count', 0)
            if 'cycle_capacity_ah' in dynamic:
                pack_data['view_cycle_capacity'] = dynamic['cycle_capacity_ah']
            pack_data['view_SOH'] = dynamic.get('soh', 0.0)

            if 'total_runtime_s' in dynamic:
                pack_data['view_run_time'] = dynamic['total_runtime_s']
            
            if 'battery_state' in dynamic:
                pack_data['battery_state'] = dynamic['battery_state']

            if 'charge_mos' in dynamic:
                pack_data['charge_mos_state'] = dynamic['charge_mos']
                pack_data['discharge_mos_state'] = dynamic['discharge_mos']
                pack_data['balance_mos_state'] = dynamic['balance_mos']

            mappings = {
                'cell_exist_state': 'view_cell_exist_state',
                'wire_alarm': 'view_wire_alarm',
                'alarm_bits': 'view_alarm_bits',
                'precharge_state': 'view_precharge_state',
                'user_alarm_1': 'view_user_alarm_1',
                'time_de_ocpr': 'view_time_de_ocpr',
                'time_de_scpr': 'view_time_de_scpr',
                'time_ch_ocpr': 'view_time_ch_ocpr',
                'time_ch_uvpr': 'view_time_ch_uvpr',
                'time_uvpr': 'view_time_uvpr',
                'time_ovpr': 'view_time_ovpr',
                'temp_sensor_presence': 'view_temp_sensor_presence',
                'heating_state': 'view_heating_state',
                'time_emergency': 'view_time_emergency',
                'vol_bat_cur_correct': 'view_vol_bat_cur_correct',
                'vol_charge_cur': 'view_vol_charge_cur',
                'vol_discharge_cur': 'view_vol_discharge_cur',
                'bat_vol_correct': 'view_bat_vol_correct',
                'heat_current_a': 'view_heat_current',
                'charger_plugged': 'view_charger_plugged',
                'sys_run_ticks': 'view_sys_run_ticks',
                'rtc_time': 'view_rtc_time',
                'fault_count': 'view_fault_count',
                'time_enter_sleep': 'view_time_enter_sleep',
                'pcl_module_sta': 'view_pcl_module_sta'
            }
            for dyn_k, pac_k in mappings.items():
                if dyn_k in dynamic:
                    pack_data[pac_k] = dynamic[dyn_k]

            # SETUP Data Mapping
            if setup:
                setup_mappings = {
                    'vol_smart_sleep': 'view_vol_smart_sleep',
                    'vol_cell_uvp': 'view_vol_cell_uvp',
                    'vol_cell_uvpr': 'view_vol_cell_uvpr',
                    'vol_cell_ovp': 'view_vol_cell_ovp',
                    'vol_cell_ovpr': 'view_vol_cell_ovpr',
                    'vol_balan_trig': 'view_vol_balan_trig',
                    'vol_soc_100': 'view_vol_soc_100',
                    'vol_soc_0': 'view_vol_soc_0',
                    'vol_bat_uvp': 'view_vol_bat_uvp',
                    'vol_bat_ovp': 'view_vol_bat_ovp',
                    'vol_sys_pwr_off': 'view_vol_sys_pwr_off',
                    'cur_bat_c_oc': 'view_cur_bat_c_oc',
                    'tim_bat_c_ocp_dly': 'view_tim_bat_c_ocp_dly',
                    'tim_bat_c_ocpr_dly': 'view_tim_bat_c_ocpr_dly',
                    'cur_bat_dc_oc': 'view_cur_bat_dc_oc',
                    'tim_bat_dc_ocp_dly': 'view_tim_bat_dc_ocp_dly',
                    'tim_bat_dc_ocpr_dly': 'view_tim_bat_dc_ocpr_dly',
                    'tim_bat_scpr_dly': 'view_tim_bat_scpr_dly',
                    'cur_balan_max': 'view_cur_balan_max',
                    'tmp_bat_cot': 'view_tmp_bat_cot',
                    'tmp_bat_cotpr': 'view_tmp_bat_cotpr',
                    'tmp_bat_dot': 'view_tmp_bat_dot',
                    'tmp_bat_dotpr': 'view_tmp_bat_dotpr',
                    'tmp_bat_cut': 'view_tmp_bat_cut',
                    'tmp_bat_cutpr': 'view_tmp_bat_cutpr',
                    'tmp_mos_otp': 'view_tmp_mos_otp',
                    'tmp_mos_otpr': 'view_tmp_mos_otpr',
                    'cell_count': 'view_setup_cell_count',
                    'bat_charge_en': 'view_bat_charge_en',
                    'bat_discharge_en': 'view_bat_discharge_en',
                    'balan_en': 'view_balan_en',
                    'cap_bat_cell': 'view_cap_bat_cell',
                    'scp_delay': 'view_scp_delay',
                    'vol_start_balan': 'view_vol_start_balan',
                    'dev_addr': 'view_dev_addr',
                    'tim_precharge': 'view_tim_precharge',
                    'func_bit_field': 'view_func_bit_field',
                    'tim_smart_sleep': 'view_tim_smart_sleep'
                }
                for set_k, pac_k in setup_mappings.items():
                    if set_k in setup:
                        pack_data[pac_k] = setup[set_k]
                
                if 'wire_res_calib' in setup:
                    pack_data['wire_res_calib'] = setup['wire_res_calib']

            # Version info
            if static:
                pack_data['hardware_version'] = static.get('hardware_version', '')
                pack_data['software_version'] = static.get('software_version', '')
            else:
                pack_data['hardware_version'] = ''
                pack_data['software_version'] = ''

            pack_list.append(pack_data)

        self.logger.debug(f"Finished getting JK BMS analog data: {pack_list}")
        return pack_list

    # ---------------------------------------------------------------------------
    # JK-native data (NEW pipeline — NOT PACE-compatible)
    # ---------------------------------------------------------------------------

    def get_jk_native_data(self):
        """
        Get all analog data from JK BMS in JK-native format.

        Returns a list of dicts with clean JK key names (no 'view_' prefix).
        Unlike get_analog_data(), this does NOT convert to PACE-compatible format.
        """
        self.logger.debug("Getting JK BMS native data")

        dynamic_results, setup_results, static_results = self.get_all_frames_data()
        if not dynamic_results:
            self.logger.warning("Failed to get dynamic data, retrying once...")
            import time
            time.sleep(0.5)
            dyn2, set2, stat2 = self.get_all_frames_data()
            dynamic_results.update(dyn2)
            setup_results.update(set2)
            static_results.update(stat2)
            if not dynamic_results:
                self.logger.error("Failed to get dynamic data after retry")
                return []

        pack_list = []

        for pack_id, dynamic in dynamic_results.items():
            static = static_results.get(pack_id) if static_results else None
            setup = setup_results.get(pack_id) if setup_results else None
            data = {}
            data['pack_id'] = pack_id

            # Cell voltages
            cells = dynamic.get('cell_voltages', [])
            data['cell_voltages'] = cells
            data['num_cells'] = len(cells)
            if cells:
                data['cell_voltage_max'] = max(cells)
                data['cell_voltage_min'] = min(cells)
                data['cell_voltage_diff'] = max(cells) - min(cells)

            # Temperatures (battery NTCs only)
            temps = []
            for key in ['temp_bat1', 'temp_bat2', 'temp_bat3', 'temp_bat4', 'temp_bat5']:
                val = dynamic.get(key)
                if val is not None:
                    temps.append(round(val, 1))
            data['temperatures'] = temps
            data['num_temps'] = len(temps)

            mos_temp = dynamic.get('temp_mos')
            if mos_temp is not None:
                data['temp_mos'] = round(mos_temp, 1)

            # Electrical
            data['current'] = dynamic.get('current_a', 0.0)
            data['voltage'] = dynamic.get('voltage_v', 0.0)
            data['power'] = dynamic.get('power_kw', 0.0)

            # Capacity / SOC
            data['soc'] = dynamic.get('soc', 0.0)
            data['remain_capacity'] = dynamic.get('remain_capacity_ah', 0.0)
            data['full_capacity'] = dynamic.get('full_capacity_ah', 0.0)
            data['design_capacity'] = data['full_capacity']
            data['cycle_count'] = dynamic.get('cycle_count', 0)
            data['soh'] = dynamic.get('soh', 0.0)

            # Balance
            data['balance_current'] = dynamic.get('balance_current_a', 0.0)

            # MOS states
            data['charge_mos'] = dynamic.get('charge_mos', False)
            data['discharge_mos'] = dynamic.get('discharge_mos', False)
            data['balance_mos'] = dynamic.get('balance_mos', False)

            # Cumulative energy
            power_kw = dynamic.get('power_kw', 0.0)
            charged, discharged = self.calculate_cumulative_energy(pack_id, power_kw)
            data['energy_charged'] = round(charged, 2)
            data['energy_discharged'] = round(discharged, 2)

            # Advanced details (requested by user)
            if 'cell_resistances' in dynamic:
                data['cell_resistances'] = dynamic['cell_resistances']
            if 'wire_alarm' in dynamic:
                data['wire_alarm'] = dynamic['wire_alarm']
            data['precharge_state'] = bool(dynamic.get('precharge_state', 0))
            if 'user_alarm_1' in dynamic:
                data['user_alarm_1'] = dynamic['user_alarm_1']
            if 'total_runtime_s' in dynamic:
                data['total_runtime'] = round(dynamic['total_runtime_s'] / 3600.0, 2)
            if 'temp_sensor_presence' in dynamic:
                presence = dynamic['temp_sensor_presence']
                data['temp_sensor_mos_ok'] = bool(presence & (1 << 0))
                data['temp_sensor_bat1_ok'] = bool(presence & (1 << 1))
                data['temp_sensor_bat2_ok'] = bool(presence & (1 << 2))
                data['temp_sensor_bat3_ok'] = bool(presence & (1 << 3))
                data['temp_sensor_bat4_ok'] = bool(presence & (1 << 4))
                data['temp_sensor_bat5_ok'] = bool(presence & (1 << 5))
            data['heating_state'] = bool(dynamic.get('heating_state', 0))
            if 'heat_current_a' in dynamic:
                data['heat_current'] = dynamic['heat_current_a']
            data['charger_plugged'] = bool(dynamic.get('charger_plugged', 0))
            if 'sys_run_ticks' in dynamic:
                # SysRunTicks is in 0.1s units
                total_seconds = dynamic['sys_run_ticks'] // 10
                days = total_seconds // 86400
                hours = (total_seconds % 86400) // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                data['system_uptime'] = f"{days}d {hours}h {minutes}m {seconds}s"
            if 'rtc_time' in dynamic:
                import datetime
                try:
                    epoch = datetime.datetime(2020, 1, 1)
                    dt = epoch + datetime.timedelta(seconds=dynamic['rtc_time'])
                    data['bms_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    data['bms_time'] = str(dynamic['rtc_time'])
            if 'fault_count' in dynamic:
                data['fault_count'] = dynamic['fault_count']
            if 'time_enter_sleep' in dynamic:
                data['time_enter_sleep_h'] = round(dynamic['time_enter_sleep'] / 3600.0, 2)
            data['pcl_module_sta'] = bool(dynamic.get('pcl_module_sta', 0))

            # Setup / Config info
            if setup:
                # Decode func_bit_field if present
                if 'func_bit_field' in setup:
                    fbits = setup['func_bit_field']
                    setup['func_heat_en'] = bool(fbits & (1 << 0))
                    setup['func_disable_temp_sensor'] = bool(fbits & (1 << 1))
                    setup['func_gps_heartbeat'] = bool(fbits & (1 << 2))
                    setup['func_port_switch_rs485'] = bool(fbits & (1 << 3))
                    setup['func_lcd_always_on'] = bool(fbits & (1 << 4))
                    setup['func_special_charger'] = bool(fbits & (1 << 5))
                    setup['func_smart_sleep'] = bool(fbits & (1 << 6))
                    setup['func_disable_pcl_module'] = bool(fbits & (1 << 7))
                    setup['func_timed_stored_data'] = bool(fbits & (1 << 8))
                    setup['func_charging_float_mode'] = bool(fbits & (1 << 9))
                data['settings'] = setup

            # Version info
            if static:
                data['hardware_version'] = static.get('hardware_version', '')
                data['software_version'] = static.get('software_version', '')
            else:
                data['hardware_version'] = ''
                data['software_version'] = ''

            pack_list.append(data)

        self.logger.debug(f"Finished getting JK BMS native data: {pack_list}")
        return pack_list

    def get_warning_data(self, pack_number=None):
        """
        Get warning/alarm data from JK BMS.
        Returns list of pack warning dicts compatible with PACE BMS format.
        """
        self.logger.debug("Starting to get JK BMS warning data")

        dynamic_results, _, _ = self.get_all_frames_data()
        if not dynamic_results:
            self.logger.warning("Failed to get warning data, retrying once...")
            import time
            time.sleep(0.5)
            dynamic_results, _, _ = self.get_all_frames_data()

        warning_data = []
        for pack_id, dynamic in dynamic_results.items():
            raw_alarm = dynamic.get('alarm_bits', 0)
            decoded = self._decode_alarms(raw_alarm)
            alarm_bits = decoded.get('alarms', {})

            pack_warning = {
                'pack_id': pack_id,
                'protect_state_1': {
                    'protect_short_circuit': alarm_bits.get('Battery SCP', False),
                    'protect_high_discharge_current': alarm_bits.get('Discharge OCP', False),
                    'protect_high_charge_current': alarm_bits.get('Charge OCP', False),
                    'protect_low_total_voltage': alarm_bits.get('Battery UVP', False),
                    'protect_high_total_voltage': alarm_bits.get('Battery OVP', False),
                    'protect_low_cell_voltage': alarm_bits.get('Cell UVP', False),
                    'protect_high_cell_voltage': alarm_bits.get('Cell OVP', False),
                },
                'protect_state_2': {
                    'protect_low_charge_temp': alarm_bits.get('Charge low-temperature protection', False),
                    'protect_high_charge_temp': alarm_bits.get('Charge over-temperature', False),
                    'protect_high_MOS_temp': alarm_bits.get('MOS over-temperature protection', False),
                    'protect_high_discharge_temp': alarm_bits.get('Discharge over-temperature', False),
                },
                'fault_state': {
                    'fault_cell': alarm_bits.get('Cell qty mismatch', False),
                    'fault_NTC': alarm_bits.get('Temperature sensor anomaly', False) or alarm_bits.get('Bat temp sensor anomaly', False),
                },
            }
            warning_data.append(pack_warning)

        self.logger.debug(f"Finished getting JK BMS warning data: {warning_data}")
        return warning_data

    # ---------------------------------------------------------------------------
    # MQTT Publishing (compatible interface with original code)
    # ---------------------------------------------------------------------------
    def publish_analog_data_mqtt(self, pack_number=None):
        """
        Publish analog data to MQTT.

        When self.ha_comm_jk is set (HA_MQTT_JK instance), uses JK-native
        entity naming. Otherwise falls back to PACE-compatible naming
        via self.ha_comm (backward compatibility path).
        """

        # ----- JK-native pipeline -----
        if self.ha_comm_jk:
            retry_count = 0
            data = []
            while retry_count < 3:
                data = self.get_jk_native_data()
                if data:
                    break
                retry_count += 1
                import time
                time.sleep(0.5)

            if not data:
                self.logger.error("Failed to get JK native data after retries")
                return

            self.ha_comm_jk.publish_analog_data(data)
            return

        # ----- Legacy PACE-compatible pipeline (unchanged) -----
        units = {
            'view_num_cells': 'cells',
            'cell_voltages': 'mV',
            'cell_voltage_max': 'mV',
            'cell_voltage_min': 'mV',
            'cell_voltage_max_index': '',
            'cell_voltage_min_index': '',
            'cell_voltage_diff': 'mV',
            'view_num_temps': 'NTCs',
            'temperatures': '°C',
            'view_current': 'A',
            'view_voltage': 'V',
            'view_remain_capacity': 'Ah',
            'view_full_capacity': 'Ah',
            'view_cycle_number': 'cycles',
            'view_design_capacity': 'Ah',
            'view_power': 'kW',
            'view_energy_charged': 'Wh',
            'view_energy_discharged': 'Wh',
            'view_SOH': '%',
            'view_SOC': '%',
            'view_balance_current': 'A',
            'hardware_version': '',
            'software_version': '',
        }

        icons = {
            'total_packs_num': 'mdi:database',
            'total_full_capacity': 'mdi:battery-high',
            'total_remain_capacity': 'mdi:battery-clock',
            'total_current': 'mdi:current-dc',
            'total_SOC': 'mdi:battery-70',
            'total_voltage': 'mdi:sine-wave',
            'total_power': 'mdi:battery-charging',
            'total_SOH': 'mdi:battery-plus-variant',
            'total_energy_charged': 'mdi:battery-positive',
            'total_energy_discharged': 'mdi:battery-negative',
            'total_cell_voltage_max': 'mdi:align-vertical-top',
            'total_cell_voltage_min': 'mdi:align-vertical-bottom',
            'total_cell_voltage_diff': 'mdi:format-align-middle',
            'view_num_cells': 'mdi:database',
            'cell_voltages': 'mdi:sine-wave',
            'cell_voltage_max': 'mdi:align-vertical-top',
            'cell_voltage_min': 'mdi:align-vertical-bottom',
            'cell_voltage_max_index': 'mdi:database',
            'cell_voltage_min_index': 'mdi:database',
            'cell_voltage_diff': 'mdi:format-align-middle',
            'view_num_temps': 'mdi:database',
            'temperatures': 'mdi:thermometer',
            'view_current': 'mdi:current-dc',
            'view_voltage': 'mdi:sine-wave',
            'view_remain_capacity': 'mdi:battery-clock',
            'view_full_capacity': 'mdi:battery-high',
            'view_cycle_number': 'mdi:battery-sync',
            'view_design_capacity': 'mdi:battery-high',
            'view_power': 'mdi:battery-charging',
            'view_energy_charged': 'mdi:battery-positive',
            'view_energy_discharged': 'mdi:battery-negative',
            'view_SOH': 'mdi:battery-plus-variant',
            'view_SOC': 'mdi:battery-70',
            'random_number': 'mdi:battery-70',
            'view_balance_current': 'mdi:scale-balance',
            'hardware_version': 'mdi:chip',
            'software_version': 'mdi:application-cog',
        }

        deviceclasses = {
            'total_packs_num': 'null',
            'total_full_capacity': 'null',
            'total_remain_capacity': 'null',
            'total_current': 'current',
            'total_SOC': 'battery',
            'total_voltage': 'voltage',
            'total_power': 'power',
            'total_SOH': 'null',
            'total_energy_charged': 'energy',
            'total_energy_discharged': 'energy',
            'total_cell_voltage_max': 'voltage',
            'total_cell_voltage_min': 'voltage',
            'total_cell_voltage_diff': 'voltage',
            'cell_voltages': 'voltage',
            'cell_voltage_max': 'voltage',
            'cell_voltage_min': 'voltage',
            'cell_voltage_max_index': 'null',
            'cell_voltage_min_index': 'null',
            'cell_voltage_diff': 'voltage',
            'temperatures': 'temperature',
            'view_num_cells': 'null',
            'view_num_temps': 'null',
            'view_current': 'current',
            'view_voltage': 'voltage',
            'view_remain_capacity': 'null',
            'view_full_capacity': 'null',
            'view_cycle_number': 'null',
            'view_design_capacity': 'null',
            'view_energy_charged': 'energy',
            'view_energy_discharged': 'energy',
            'view_power': 'power',
            'view_SOH': 'null',
            'view_SOC': 'null',
            'random_number': 'null',
            'view_balance_current': 'current',
            'hardware_version': 'null',
            'software_version': 'null',
        }

        stateclasses = {
            'total_packs_num': 'measurement',
            'total_full_capacity': 'measurement',
            'total_remain_capacity': 'measurement',
            'total_current': 'measurement',
            'total_SOC': 'measurement',
            'total_voltage': 'measurement',
            'total_power': 'measurement',
            'total_SOH': 'measurement',
            'total_energy_charged': 'total',
            'total_energy_discharged': 'total',
            'total_cell_voltage_max': 'measurement',
            'total_cell_voltage_min': 'measurement',
            'total_cell_voltage_diff': 'measurement',
            'view_num_cells': 'measurement',
            'cell_voltages': 'measurement',
            'cell_voltage_max': 'measurement',
            'cell_voltage_min': 'measurement',
            'cell_voltage_max_index': 'measurement',
            'cell_voltage_min_index': 'measurement',
            'cell_voltage_diff': 'measurement',
            'view_num_temps': 'measurement',
            'temperatures': 'measurement',
            'view_current': 'measurement',
            'view_voltage': 'measurement',
            'view_remain_capacity': 'measurement',
            'view_full_capacity': 'measurement',
            'view_cycle_number': 'measurement',
            'view_design_capacity': 'measurement',
            'view_energy_charged': 'total',
            'view_energy_discharged': 'total',
            'view_SOH': 'measurement',
            'view_SOC': 'measurement',
            'random_number': 'measurement',
            'view_balance_current': 'measurement',
            'hardware_version': 'null',
            'software_version': 'null',
        }

        while True:
            analog_data = self.get_analog_data(pack_number)
            if analog_data:
                break

        total_packs_num = len(analog_data)
        if total_packs_num < 1:
            self.logger.error("No packs found")
            return None

        self.ha_comm.publish_sensor_state(total_packs_num, 'packs', "total_packs_num")
        self.ha_comm.publish_sensor_discovery("total_packs_num", "packs", icons['total_packs_num'], deviceclasses['total_packs_num'], stateclasses['total_packs_num'])

        total_full_capacity = round(sum(d.get('view_full_capacity', 0) for d in analog_data), 2)
        self.ha_comm.publish_sensor_state(total_full_capacity, 'Ah', "total_full_capacity")
        self.ha_comm.publish_sensor_discovery("total_full_capacity", "Ah", icons['total_full_capacity'], deviceclasses['total_full_capacity'], stateclasses['total_full_capacity'])

        total_remain_capacity = round(sum(d.get('view_remain_capacity', 0) for d in analog_data), 2)
        self.ha_comm.publish_sensor_state(total_remain_capacity, 'Ah', "total_remain_capacity")
        self.ha_comm.publish_sensor_discovery("total_remain_capacity", "Ah", icons['total_remain_capacity'], deviceclasses['total_remain_capacity'], stateclasses['total_remain_capacity'])

        total_current = round(sum(d.get('view_current', 0) for d in analog_data), 2)
        self.ha_comm.publish_sensor_state(total_current, 'A', "total_current")
        self.ha_comm.publish_sensor_discovery("total_current", "A", icons['total_current'], deviceclasses['total_current'], stateclasses['total_current'])

        total_soc = round(total_remain_capacity / total_full_capacity * 100, 1) if total_full_capacity > 0 else 0
        self.ha_comm.publish_sensor_state(total_soc, '%', "total_SOC")
        self.ha_comm.publish_sensor_discovery("total_SOC", "%", icons['total_SOC'], deviceclasses['total_SOC'], stateclasses['total_SOC'])

        if self.if_random:
            import random
            random_number = random.randint(1, 100)
            self.ha_comm.publish_sensor_state(random_number, 'R', "random_number")
            self.ha_comm.publish_sensor_discovery("random_number", "R", icons['random_number'], deviceclasses['random_number'], stateclasses['random_number'])

        for pack in analog_data:
            pack_i = pack.get('pack_id', 0) + self.pack_index_start
            for key, value in pack.items():
                if key == 'pack_id':
                    continue
                unit = units.get(key, '')
                icon = icons.get(key, '')
                deviceclass = deviceclasses.get(key, '')
                stateclass = stateclasses.get(key, '')

                if key == 'cell_voltages':
                    cell_i = 0
                    for cell_voltage in value:
                        cell_i += 1
                        self.ha_comm.publish_sensor_state(cell_voltage, unit, f"pack_{pack_i:02}_cell_voltage_{cell_i:02}")
                        self.ha_comm.publish_sensor_discovery(f"pack_{pack_i:02}_cell_voltage_{cell_i:02}", unit, icon, deviceclass, stateclass)

                elif key == 'temperatures':
                    temperature_i = 0
                    for temperature in value:
                        temperature_i += 1
                        self.ha_comm.publish_sensor_state(temperature, unit, f"pack_{pack_i:02}_temperature_{temperature_i:02}")
                        self.ha_comm.publish_sensor_discovery(f"pack_{pack_i:02}_temperature_{temperature_i:02}", unit, icon, deviceclass, stateclass)

                else:
                    if key in ['hardware_version', 'software_version']:
                        self.logger.debug(f"Preparing to publish {key}: value='{value}', unit='{unit}', icon='{icon}'")
                    self.ha_comm.publish_sensor_state(value, unit, f"pack_{pack_i:02}_{key}")
                    self.ha_comm.publish_sensor_discovery(f"pack_{pack_i:02}_{key}", unit, icon, deviceclass, stateclass)

    def publish_warning_data_mqtt(self, pack_number=None):
        """
        Publish warning data to MQTT.

        When self.ha_comm_jk is set (HA_MQTT_JK instance), uses JK-native
        entity naming. Otherwise falls back to PACE-compatible naming
        via self.ha_comm (backward compatibility path).
        """

        # ----- JK-native pipeline -----
        if self.ha_comm_jk:
            warn_data = self.get_warning_data(pack_number)

            if not warn_data:
                self.logger.error("No warning data to publish")
                return

            self.ha_comm_jk.publish_warning_data(warn_data)
            return

        # ----- Legacy PACE-compatible pipeline (unchanged) -----
        warn_data = self.get_warning_data(pack_number)

        total_packs_num = len(warn_data)
        if total_packs_num < 1:
            self.logger.error("No packs found")
            return None

        for pack in warn_data:
            pack_i = pack.get('pack_id', 0) + self.pack_index_start
            for key, value in pack.items():
                if key == 'pack_id':
                    continue
                if key == 'cell_voltage_warnings':
                    cell_i = 0
                    icon = "mdi:battery-heart-variant"
                    for cell_voltage_warning in value:
                        cell_i += 1
                        self.ha_comm.publish_warn_state(cell_voltage_warning, f"pack_{pack_i:02}_cell_voltage_warning_{cell_i:02}")
                        self.ha_comm.publish_warn_discovery(f"pack_{pack_i:02}_cell_voltage_warning_{cell_i:02}", icon)

                elif key == 'protect_state_1':
                    icon = "mdi:battery-alert"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}", icon)

                elif key == 'fault_state':
                    icon = "mdi:alert"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}", icon)
