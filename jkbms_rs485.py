#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import logging

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

    def __init__(self, bms_comm, ha_comm, bms_type, data_refresh_interval, debug, if_random):
        self.bms_comm = bms_comm
        self.ha_comm = ha_comm
        self.bms_type = bms_type
        self.data_refresh_interval = data_refresh_interval
        self.debug = debug
        self.if_random = if_random

        # Cumulative energy variables
        self.total_energy_charged = 0.0
        self.total_energy_discharged = 0.0
        self.last_energy_time = None

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # JK BMS registers for data queries (Modbus FC 0x10 write with 0x0000)
        self.REG_STATIC = 0x161C    # Trame 1 - Static data (version, serial, etc.)
        self.REG_SETUP  = 0x161E    # Trame 2 - Setup/Config data
        self.REG_DYNAMIC = 0x1620   # Trame 3 - Dynamic data (cells, current, SOC, etc.)
        self.REG_ALARM  = 0x12A0    # Alarm register (FC 0x03 read, count 2)

        # Slave address: default 0x01 as used by reference implementation
        self.slave_address = 0x01

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
    # Energy calculation (same as original, uses time intervals)
    # ---------------------------------------------------------------------------
    def calculate_cumulative_energy(self, current_power_kw):
        import time
        current_time = time.time()
        if self.last_energy_time is None:
            self.last_energy_time = current_time
            return self.total_energy_charged, self.total_energy_discharged
        time_interval = current_time - self.last_energy_time
        self.last_energy_time = current_time
        if time_interval <= 0 or time_interval > 300:
            self.logger.warning(f"Abnormal time interval: {time_interval}s, skipping energy calculation")
            return self.total_energy_charged, self.total_energy_discharged
        if current_power_kw is not None:
            energy_delta = abs(current_power_kw) * time_interval * 1000 / 3600
            if current_power_kw >= 0:
                self.total_energy_charged += energy_delta
                self.logger.debug(f"Charge energy delta: {energy_delta:.3f}Wh, cumulative: {self.total_energy_charged:.3f}Wh")
            else:
                self.total_energy_discharged += energy_delta
                self.logger.debug(f"Discharge energy delta: {energy_delta:.3f}Wh, cumulative: {self.total_energy_discharged:.3f}Wh")
        return self.total_energy_charged, self.total_energy_discharged

    def reset_cumulative_energy(self):
        self.total_energy_charged = 0.0
        self.total_energy_discharged = 0.0
        self.last_energy_time = None
        self.logger.info("Cumulative energy counters have been reset")

    # ---------------------------------------------------------------------------
    # Command builders
    # ---------------------------------------------------------------------------
    def build_read_command(self, register_address, register_count=1):
        """
        Build Modbus FC 0x03 (Read Holding Registers) command.
        Used for alarm reads (0x12A0).
        """
        command_frame = struct.pack('>BBHH',
                                    self.slave_address,
                                    0x03,               # Function code: Read Holding Registers
                                    register_address,
                                    register_count)
        crc = self.calculate_crc16_modbus(command_frame)
        command = command_frame + struct.pack('<H', crc)
        self.logger.debug(f"Read command: {command.hex().upper()}")
        return command

    def build_write_command(self, register_address):
        """
        Build Modbus FC 0x10 (Write Multiple Registers) command with value 0x0000.
        Used to query JK BMS data frames (0x161C, 0x161E, 0x1620).
        """
        command_frame = struct.pack('>BBHHBB',
                                    self.slave_address,
                                    0x10,               # Function code: Write Multiple Registers
                                    register_address,
                                    0x0001,             # Quantity: 1 register
                                    0x02,               # Byte count: 2 bytes
                                    0x00)               # Data high byte
        # Append data low byte separately for clarity
        command_frame += struct.pack('B', 0x00)          # Data low byte
        crc = self.calculate_crc16_modbus(command_frame)
        command = command_frame + struct.pack('<H', crc)
        self.logger.debug(f"Write query command for 0x{register_address:04X}: {command.hex().upper()}")
        return command

    # ---------------------------------------------------------------------------
    # Passive data reception (BMS broadcasts 55AA frames automatically)
    # ---------------------------------------------------------------------------

    def receive_55aa_frames(self, timeout=2.0):
        """
        Passively receive 55AA frames from the JK BMS broadcast stream.

        Protocol structure (from JK-BMS-RS485-Protocol.md):
          Each received block = 300-byte 55AA frame + 8-byte Modbus ACK = 308 bytes total
          byte[4] = Pack ID (NOT frame type)
          The trailing 8-byte Modbus ACK contains the register address that triggered this frame:
            bytes[292-293] of the 300-byte frame = offset 292 within the 55AA block
            In the 308-byte block: bytes[300+2..300+3] = register address
              0x1620 → Dynamic data frame  (Trame 3)
              0x161E → Setup/Config frame  (Trame 2)
              0x161C → Static data frame   (Trame 1)

        Returns:
            list of tuples (frame_300bytes, reg_addr) for each complete 55AA block found
        """
        raw_data = self.bms_comm.receive_jkbms_passive(timeout)
        if not raw_data:
            self.logger.warning("receive_55aa_frames: no data received from BMS (raw_data is None/empty)")
            return []

        # Always print full raw hex at WARNING level so it shows without debug mode
        hex_lines = '\n'.join(
            '  {:04X}: {:48s}  |{}|'.format(
                i,
                ' '.join(f'{b:02X}' for b in raw_data[i:i+16]),
                ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw_data[i:i+16])
            )
            for i in range(0, len(raw_data), 16)
        )
        self.logger.warning(
            f"receive_55aa_frames: got {len(raw_data)} bytes raw data:\n{hex_lines}"
        )

        BLOCK_SIZE = 308   # 300-byte 55AA frame + 8-byte Modbus ACK
        FRAME_SIZE = 300   # Pure 55AA frame data

        frames = []  # list of (frame_300, reg_addr)
        search_start = 0
        while search_start < len(raw_data):
            start = raw_data.find(b'\x55\xAA', search_start)
            if start < 0:
                break

            if start + BLOCK_SIZE <= len(raw_data):
                block = raw_data[start:start + BLOCK_SIZE]
                frame = block[:FRAME_SIZE]          # 300-byte 55AA data
                # Modbus ACK starts at offset 300: [slave][0x10][reg_hi][reg_lo]...
                reg_hi = block[302]
                reg_lo = block[303]
                reg_addr = (reg_hi << 8) | reg_lo
                pack_id = frame[4] if len(frame) > 4 else 0
                self.logger.warning(
                    f"receive_55aa_frames: block at offset {start}, "
                    f"pack_id={pack_id}, reg=0x{reg_addr:04X} "
                    f"({'DYNAMIC' if reg_addr == 0x1620 else 'SETUP' if reg_addr == 0x161E else 'STATIC' if reg_addr == 0x161C else 'UNKNOWN'})"
                )
                frames.append((frame, reg_addr))
                search_start = start + BLOCK_SIZE
            else:
                remaining = len(raw_data) - start
                self.logger.warning(
                    f"receive_55aa_frames: 55AA marker at offset {start}, "
                    f"only {remaining} bytes remain (need {BLOCK_SIZE}) — incomplete block"
                )
                break

        if frames:
            self.logger.warning(f"receive_55aa_frames: extracted {len(frames)} 55AA block(s) from {len(raw_data)} bytes")
        else:
            self.logger.warning(f"receive_55aa_frames: NO 55AA block found in {len(raw_data)} bytes")

        return frames

    def send_and_receive(self, command):
        """
        Legacy method: send a command and receive response.
        Kept for backward compatibility. Prefer passive receive_55aa_frames().
        """
        self.bms_comm.flush_jkbms_buffer()
        if not self.bms_comm.send_data(command):
            self.logger.error("Failed to send command")
            return None
        response = self.bms_comm.receive_jkbms_raw()
        return response

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

        # ---- MOS temp: int16le at offset 144 (/10 = °C) ----
        if 145 < len(data):
            raw_mos = struct.unpack_from('<h', data, 144)[0]
            if -500 < raw_mos < 1500:
                result['temp_mos'] = raw_mos / 10.0

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

        # ---- Battery temp sensors: int16le at 162, 164, 254, 258 (/10 = °C) ----
        temps = {
            'temp_bat1': 162,
            'temp_bat2': 164,
            'temp_bat3': 254,
            'temp_bat4': 258,
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

        # ---- SOC: uint8 at offset 173 (%) ----
        if 173 < len(data):
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

        # ---- SOH: uint8 at offset 190 (%) ----
        if 190 < len(data):
            soh = data[190]
            if 0 < soh <= 100:
                result['soh'] = float(soh)

        # ---- Total runtime: uint32le at offset 194 (s) ----
        if 198 <= len(data):
            runtime = struct.unpack_from('<I', data, 194)[0]
            result['total_runtime_s'] = runtime

        # ---- MOS status: uint8 at 198 (charge), 199 (discharge), 200 (balance) ----
        if 201 < len(data):
            result['charge_mos'] = bool(data[198])
            result['discharge_mos'] = bool(data[199])
            result['balance_mos'] = bool(data[200])

        # ---- Total voltage (standard precision): uint16le at 234 (/100 = V) ----
        if 236 <= len(data):
            raw_sv = struct.unpack_from('<H', data, 234)[0]
            if raw_sv > 0:
                # Only set if voltage_v wasn't set from offset 150
                if 'voltage_v' not in result:
                    result['voltage_v'] = raw_sv / 100.0

        # ---- Fault record count: uint8 at offset 266 ----
        if 266 < len(data):
            result['fault_count'] = int(data[266])

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

    def parse_alarm_response(self, response):
        """
        Parse alarm response from Modbus FC 0x03 read of 0x12A0.

        Standard Modbus RTU response format:
        [0]: Slave ID
        [1]: 0x03 (FC)
        [2]: 0x04 (byte count)
        [3-6]: 32-bit alarm value (big-endian)
        [7-8]: CRC
        """
        if not response or len(response) < 9:
            self.logger.warning("Alarm response too short")
            return None

        # Validate CRC
        data_no_crc = response[:-2]
        received_crc = struct.unpack('<H', response[-2:])[0]
        calc_crc = self.calculate_crc16_modbus(data_no_crc)
        if received_crc != calc_crc:
            self.logger.error(f"Alarm CRC failed: received={received_crc:04X}, calculated={calc_crc:04X}")
            # Try parsing anyway for resilience

        alarm_value = struct.unpack('>I', response[3:7])[0]
        return self._decode_alarms(alarm_value)

    def _decode_alarms(self, alarm_value):
        """Decode 32-bit alarm bitfield into structured dict."""
        alarm_bits = {
            0: "Balancing resistance too high",
            1: "MOS over-temperature protection",
            2: "Number of cells does not match parameter",
            3: "Abnormal current sensor",
            4: "Cell over-voltage protection",
            5: "Battery over-voltage protection",
            6: "Overcurrent charge protection",
            7: "Charge short-circuit protection",
            8: "Over-temperature charge protection",
            9: "Low temperature charge protection",
            10: "Internal communication anomaly",
            11: "Cell under-voltage protection",
            12: "Battery under-voltage protection",
            13: "Overcurrent discharge protection",
            14: "Discharge short-circuit protection",
            15: "Over-temperature discharge protection",
            16: "Charge MOS anomaly",
            17: "Discharge MOS anomaly",
            18: "GPS disconnected",
            19: "Please modify the authorization password in time",
            20: "Discharge activation failure",
            21: "Battery over-temperature alarm",
            22: "Temperature sensor anomaly",
            23: "Parallel module anomaly",
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
    def get_dynamic_data(self):
        """
        Read JK BMS dynamic data from passively received broadcast.
        The BMS automatically broadcasts 55AA frames — no command needed.

        Dynamic frames are identified by the trailing Modbus ACK register = 0x1620.
        byte[4] in the 55AA header is the Pack ID, NOT a frame type indicator.

        Returns parsed 55AA dynamic frame dict or None.
        """
        def _try_frames(frame_list):
            for frame, reg_addr in frame_list:
                if reg_addr != 0x1620:
                    self.logger.debug(
                        f"get_dynamic_data: skipping reg=0x{reg_addr:04X} (not dynamic 0x1620)"
                    )
                    continue
                result = self.parse_jkbms_55aa_frame(frame)
                if result.get('cell_voltages'):
                    if self.debug and self.logger.isEnabledFor(logging.DEBUG):
                        self.dump_frame_analysis(frame)
                    return result
                else:
                    self.logger.warning(
                        f"get_dynamic_data: dynamic frame (reg=0x1620) parsed but no cell_voltages found. "
                        f"pack_id={frame[4]}, result={result}"
                    )
            return None

        # First attempt
        frames = self.receive_55aa_frames(timeout=1.0)
        result = _try_frames(frames)
        if result:
            return result

        # No valid dynamic frame yet — wait for next broadcast cycle
        self.logger.debug("No dynamic 55AA frame in first read, waiting for next broadcast...")
        import time
        time.sleep(0.5)
        frames = self.receive_55aa_frames(timeout=2.0)
        result = _try_frames(frames)
        if result:
            return result

        self.logger.warning("No valid dynamic 55AA frame received after waiting")
        return None

    def get_static_data(self):
        """
        Read JK BMS static data from passively received broadcast.
        Static frames are identified by trailing ACK register 0x161C.
        Returns parsed 55AA frame dict with version info or None.
        """
        frame_list = self.receive_55aa_frames(timeout=1.0)
        for frame, reg_addr in frame_list:
            if reg_addr != 0x161C:
                continue
            result = self.parse_jkbms_static_frame(frame)
            if result:
                return result

        self.logger.debug("No static 55AA frame (reg=0x161C) in buffer")
        return None

    def get_alarm_data(self):
        """
        Read alarm/status information from passively received broadcast data.
        Additionally checks if alarm Modbus responses happen to be in the stream.
        Returns parsed alarm dict or None.
        """
        # Try to find alarm data in the passive broadcast
        raw = self.bms_comm.receive_jkbms_passive(read_timeout=1.0)
        if not raw:
            return None

        # Look for Modbus RTU response in the raw data
        # Alarm FC 0x03 response format: [slave] [0x03] [byte_cnt=4] [data...4] [CRC...2]
        alarm_response = None
        for candidate_addr in [self.slave_address, 0x0A, 0x01, 0x00]:
            pattern = bytes([candidate_addr, 0x03, 0x04])
            idx = raw.find(pattern)
            if idx >= 0 and idx + 9 <= len(raw):
                alarm_response = raw[idx:idx+9]
                self.logger.debug(f"Found alarm response at offset {idx} with addr 0x{candidate_addr:02X}")
                break

        if not alarm_response:
            self.logger.debug("No alarm data in passive broadcast stream")
            return None

        return self.parse_alarm_response(alarm_response)

    # ---------------------------------------------------------------------------
    # Main data gathering (compatible interface with original code)
    # ---------------------------------------------------------------------------
    def get_analog_data(self, pack_number=None):
        """
        Get all analog data from JK BMS.
        Returns list of pack dicts compatible with PACE BMS format.
        """
        self.logger.debug("Starting to get JK BMS analog data")

        # Query dynamic data (contains cells, current, voltage, SOC, temps)
        dynamic = self.get_dynamic_data()
        if not dynamic:
            self.logger.warning("Failed to get dynamic data, retrying once...")
            import time
            time.sleep(0.5)
            dynamic = self.get_dynamic_data()
            if not dynamic:
                self.logger.error("Failed to get dynamic data after retry")
                return None

        # Query static data for version info (best effort)
        static = self.get_static_data()

        # Build output dict compatible with PACE BMS format
        pack_data = {}

        # Cell voltages (in mV, already parsed from 55AA frame)
        cells = dynamic.get('cell_voltages', [])
        pack_data['cell_voltages'] = cells
        pack_data['view_num_cells'] = len(cells)
        if cells:
            pack_data['cell_voltage_max'] = max(cells)
            pack_data['cell_voltage_min'] = min(cells)
            pack_data['cell_voltage_max_index'] = cells.index(max(cells)) + 1
            pack_data['cell_voltage_min_index'] = cells.index(min(cells)) + 1
            pack_data['cell_voltage_diff'] = max(cells) - min(cells)
        else:
            pack_data['cell_voltage_max'] = 0
            pack_data['cell_voltage_min'] = 0
            pack_data['cell_voltage_max_index'] = 0
            pack_data['cell_voltage_min_index'] = 0
            pack_data['cell_voltage_diff'] = 0

        # Temperatures
        temps = []
        for key in ['temp_bat1', 'temp_bat2', 'temp_bat3', 'temp_bat4', 'temp_mos']:
            val = dynamic.get(key)
            if val is not None and -50 <= val <= 150:
                temps.append(round(val, 1))
        pack_data['temperatures'] = temps
        pack_data['view_num_temps'] = len(temps)

        # Current (A)
        pack_data['view_current'] = dynamic.get('current_a', 0.0)

        # Voltage (V)
        pack_data['view_voltage'] = dynamic.get('voltage_v', 0.0)

        # Power (kW)
        power_kw = dynamic.get('power_kw', 0.0)
        pack_data['view_power'] = power_kw

        # Cumulative energy
        charged_total, discharged_total = self.calculate_cumulative_energy(power_kw)
        pack_data['view_energy_charged'] = round(charged_total, 2)
        pack_data['view_energy_discharged'] = round(discharged_total, 2)

        # SOC & capacity
        pack_data['view_SOC'] = dynamic.get('soc', 0.0)
        pack_data['view_remain_capacity'] = dynamic.get('remain_capacity_ah', 0.0)
        pack_data['view_full_capacity'] = dynamic.get('full_capacity_ah', 0.0)
        pack_data['view_design_capacity'] = pack_data['view_full_capacity']
        pack_data['view_cycle_number'] = dynamic.get('cycle_count', 0)
        pack_data['view_SOH'] = dynamic.get('soh', 0.0)

        # Balance current
        pack_data['view_balance_current'] = dynamic.get('balance_current_a', 0.0)

        # Version info
        if static:
            pack_data['hardware_version'] = static.get('hardware_version', '')
            pack_data['software_version'] = static.get('software_version', '')
        else:
            pack_data['hardware_version'] = ''
            pack_data['software_version'] = ''

        pack_list = [pack_data]
        self.logger.debug(f"Finished getting JK BMS analog data: {pack_data}")
        return pack_list

    def get_warning_data(self, pack_number=None):
        """
        Get warning/alarm data from JK BMS.
        Returns list of pack warning dicts compatible with PACE BMS format.
        """
        self.logger.debug("Starting to get JK BMS warning data")

        alarm = self.get_alarm_data()
        cells = self.get_dynamic_data()

        cell_count = len(cells.get('cell_voltages', [])) if cells else 0

        alarm_bits = {}
        if alarm:
            alarm_bits = alarm.get('alarms', {})

        pack_warning = {
            'cell_number': cell_count,
            'cell_voltage_warnings': ['normal'] * cell_count,
            'temp_sensor_number': 0,
            'temp_sensor_warnings': [],
            'warn_charge_current': 'normal',
            'warn_total_voltage': 'normal',
            'warn_discharge_current': 'normal',
            'protect_state_1': {
                'protect_short_circuit': alarm_bits.get('Discharge short-circuit protection', False),
                'protect_high_discharge_current': alarm_bits.get('Overcurrent discharge protection', False),
                'protect_high_charge_current': alarm_bits.get('Overcurrent charge protection', False),
                'protect_low_total_voltage': alarm_bits.get('Battery under-voltage protection', False),
                'protect_high_total_voltage': alarm_bits.get('Battery over-voltage protection', False),
                'protect_low_cell_voltage': alarm_bits.get('Cell under-voltage protection', False),
                'protect_high_cell_voltage': alarm_bits.get('Cell over-voltage protection', False),
            },
            'protect_state_2': {
                'status_fully_charged': False,
                'protect_low_env_temp': alarm_bits.get('Low temperature charge protection', False),
                'protect_high_env_temp': alarm_bits.get('Over-temperature charge protection', False),
                'protect_high_MOS_temp': alarm_bits.get('MOS over-temperature protection', False),
                'protect_low_discharge_temp': alarm_bits.get('Low temperature charge protection', False),
                'protect_low_charge_temp': alarm_bits.get('Low temperature charge protection', False),
                'protect_high_discharge_temp': alarm_bits.get('Over-temperature discharge protection', False),
                'protect_high_charge_temp': alarm_bits.get('Over-temperature charge protection', False),
            },
            'fault_state': {
                'fault_sampling': alarm_bits.get('Abnormal current sensor', False),
                'fault_cell': alarm_bits.get('Number of cells does not match parameter', False),
                'fault_NTC': alarm_bits.get('Temperature sensor anomaly', False),
                'fault_discharge_MOS': alarm_bits.get('Discharge MOS anomaly', False),
                'fault_charge_MOS': alarm_bits.get('Charge MOS anomaly', False),
            },
            'instruction_state': {},
            'control_state': {},
            'balance_state_1': 0,
            'balance_state_2': 0,
            'warn_state_1': {},
            'warn_state_2': {},
        }

        warning_data = [pack_warning]
        self.logger.debug(f"Finished getting JK BMS warning data: {warning_data}")
        return warning_data

    # ---------------------------------------------------------------------------
    # MQTT Publishing (compatible interface with original code)
    # ---------------------------------------------------------------------------
    def publish_analog_data_mqtt(self, pack_number=None):
        """
        Publish analog data to MQTT.
        Compatible format with PACE BMS.
        """

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
            if analog_data is not None:
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

        pack_i = 0
        for pack in analog_data:
            pack_i += 1
            for key, value in pack.items():
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
        Compatible format with PACE BMS.
        """
        while True:
            warn_data = self.get_warning_data(pack_number)
            if warn_data is not None:
                break

        total_packs_num = len(warn_data)
        if total_packs_num < 1:
            self.logger.error("No packs found")
            return None

        pack_i = 0
        for pack in warn_data:
            pack_i += 1
            for key, value in pack.items():
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
