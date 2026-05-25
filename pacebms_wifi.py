import logging
import time
import socket

class PACEBMSWIFI:
    def __init__(self, bms_comm, ha_comm, bms_type, data_refresh_interval, debug, if_random):
        self.bms_comm = bms_comm
        self.ha_comm = ha_comm
        self.bms_type = bms_type
        self.data_refresh_interval = data_refresh_interval
        self.if_random = if_random

        # Configure logging
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self.buffer = ""
        self.latest_analog_data = None
        self.latest_warning_data = None

        # Cumulative energy tracking
        self.total_energy_charged = 0.0
        self.total_energy_discharged = 0.0
        self.last_energy_time = time.time()

    def hex_to_signed(self, hex_str):
        """Convert a 16-bit hexadecimal string to signed integer value."""
        raw_value = int(hex_str, 16)
        if raw_value & 0x8000:
            signed_value = -((~raw_value & 0xFFFF) + 1)
        else:
            signed_value = raw_value
        return signed_value

    def calculate_cumulative_energy(self, power):
        """Calculate cumulative energy (Wh)"""
        current_time = time.time()
        time_diff = current_time - self.last_energy_time

        if time_diff > 300:
            self.logger.warning(f"Abnormal time interval detected: {time_diff:.1f}s, resetting time base")
            self.last_energy_time = current_time
            return self.total_energy_charged, self.total_energy_discharged

        if time_diff < 1:
            return self.total_energy_charged, self.total_energy_discharged

        # power is in kW. kW * seconds / 3600 * 1000 = Wh
        energy_increment = abs(power) * time_diff / 3600 * 1000

        if power >= 0:
            self.total_energy_charged += energy_increment
        else:
            self.total_energy_discharged += energy_increment

        self.last_energy_time = current_time
        return round(self.total_energy_charged, 2), round(self.total_energy_discharged, 2)

    def interpret_warning(self, value):
        if value == 0x00:
            return 'normal'
        elif value == 0x01:
            return 'below lower limit'
        elif value == 0x02:
            return 'above upper limit'
        elif 0x80 <= value <= 0xEF:
            return 'user defined'
        elif value == 0xF0:
            return 'other fault'
        else:
            return 'unknown'

    def read_passive_frame(self, timeout=5.0):
        """Passively read from connection until we get a complete frame starting with '~' and ending with '\r'."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if '~' in self.buffer:
                soi_idx = self.buffer.index('~')
                eoi_idx = self.buffer.find('\r', soi_idx)
                if eoi_idx != -1:
                    frame = self.buffer[soi_idx:eoi_idx + 1]
                    self.buffer = self.buffer[eoi_idx + 1:]
                    return frame
                else:
                    if len(self.buffer) > 4096:
                        # Prevent buffer overflow
                        self.buffer = self.buffer[soi_idx:]
            else:
                if len(self.buffer) > 4096:
                    self.buffer = ""

            try:
                conn = self.bms_comm.bms_connection
                if not conn:
                    self.logger.warning("BMS connection is missing. Reconnecting...")
                    self.bms_comm.connect()
                    time.sleep(0.5)
                    continue

                if hasattr(conn, 'recv'):
                    conn.settimeout(0.5)
                    raw_chunk = conn.recv(2048)
                    if not raw_chunk:
                        time.sleep(0.1)
                        continue
                    chunk = raw_chunk.decode('ascii', errors='ignore')
                    self.buffer += chunk
                elif hasattr(conn, 'readline'):
                    conn.timeout = 0.5
                    raw_chunk = conn.readline()
                    if not raw_chunk:
                        time.sleep(0.1)
                        continue
                    chunk = raw_chunk.decode('ascii', errors='ignore')
                    self.buffer += chunk
                else:
                    self.logger.error("BMS connection does not support read operations")
                    time.sleep(1.0)
            except socket.timeout:
                pass
            except Exception as e:
                self.logger.error(f"Error reading passive data: {e}")
                time.sleep(0.5)
                self.bms_comm.connect()
        return None

    def process_incoming_data(self, timeout=5.0):
        """Read and parse incoming frames, routing to analog or warning."""
        frame = self.read_passive_frame(timeout)
        if not frame:
            return False

        # Clean/preprocess frame
        frame_clean = frame.strip()
        if "gobel" in frame_clean.lower():
            self.logger.debug("Received heartbeat 'gobel'")
            return True

        if frame_clean.startswith('~'):
            frame_clean = frame_clean[1:]

        actual_hex = "".join([c for c in frame_clean if c in "0123456789ABCDEFabcdef"])
        fields = [actual_hex[i:i+2] for i in range(0, len(actual_hex), 2)]

        if len(fields) < 9:
            self.logger.warning(f"Fields length too short for routing: {len(fields)}")
            return False

        # RTN/CID2 is fields[3]
        cid2 = fields[3].upper()

        if cid2 == '42':
            self.latest_analog_data = self.parse_analog_data_wifi(fields)
            self.logger.debug("Parsed analog data successfully")
            return True
        elif cid2 == '44':
            self.latest_warning_data = self.parse_warning_data_wifi(fields)
            self.logger.debug("Parsed warning data successfully")
            return True
        else:
            self.logger.warning(f"Unhandled passive CID2/RTN: {cid2}")
            return False

    def parse_analog_data_wifi(self, fields):
        """Parse analog data fields according to PCLVBattery / dataParser.js format."""
        try:
            pack_count = int(fields[7], 16)
            if pack_count <= 0:
                pack_count = 1
        except Exception:
            pack_count = 1

        offset = 8
        packs_data = []

        for pack_idx in range(pack_count):
            if offset >= len(fields):
                break

            pack_data = {}

            # Cell count
            try:
                num_cells = int(fields[offset], 16)
            except Exception:
                num_cells = 0
            offset += 1
            pack_data['view_num_cells'] = num_cells

            # Cell voltages
            cell_voltages = []
            for _ in range(num_cells):
                if offset + 1 >= len(fields):
                    break
                voltage = int(fields[offset] + fields[offset + 1], 16)
                cell_voltages.append(voltage)
                offset += 2
            pack_data['cell_voltages'] = cell_voltages

            if cell_voltages:
                cell_voltage_max = max(cell_voltages)
                cell_voltage_min = min(cell_voltages)
                pack_data['cell_voltage_max'] = cell_voltage_max
                pack_data['cell_voltage_min'] = cell_voltage_min
                pack_data['cell_voltage_max_index'] = cell_voltages.index(cell_voltage_max) + 1
                pack_data['cell_voltage_min_index'] = cell_voltages.index(cell_voltage_min) + 1
                pack_data['cell_voltage_diff'] = cell_voltage_max - cell_voltage_min
            else:
                pack_data['cell_voltage_max'] = 0
                pack_data['cell_voltage_min'] = 0
                pack_data['cell_voltage_max_index'] = 0
                pack_data['cell_voltage_min_index'] = 0
                pack_data['cell_voltage_diff'] = 0

            # Temp sensors
            if offset >= len(fields):
                break
            try:
                num_temps = int(fields[offset], 16)
            except Exception:
                num_temps = 0
            offset += 1
            pack_data['view_num_temps'] = num_temps

            # Temperatures
            temperatures = []
            for _ in range(num_temps):
                if offset + 1 >= len(fields):
                    break
                temp_raw = int(fields[offset] + fields[offset + 1], 16)
                # (temp_raw - 2730) / 10
                temp_c = round((temp_raw - 2730) / 10.0, 2)
                temperatures.append(temp_c)
                offset += 2
            pack_data['temperatures'] = temperatures

            # Pack current
            if offset + 1 >= len(fields):
                break
            current_hex = fields[offset] + fields[offset + 1]
            pack_current = self.hex_to_signed(current_hex) / 100.0
            offset += 2
            pack_data['view_current'] = pack_current

            # Pack voltage
            if offset + 1 >= len(fields):
                break
            voltage_hex = fields[offset] + fields[offset + 1]
            pack_voltage = int(voltage_hex, 16) / 1000.0
            offset += 2
            pack_data['view_voltage'] = pack_voltage

            # Calculate power (kW)
            pack_power = round(pack_voltage * pack_current / 1000.0, 4)
            pack_data['view_power'] = pack_power

            # Cumulative energy
            cumulative_charged, cumulative_discharged = self.calculate_cumulative_energy(pack_power)
            pack_data['view_energy_charged'] = cumulative_charged
            pack_data['view_energy_discharged'] = cumulative_discharged

            # Remaining capacity
            if offset + 1 >= len(fields):
                break
            remain_cap_hex = fields[offset] + fields[offset + 1]
            pack_remain_capacity = int(remain_cap_hex, 16) / 100.0
            offset += 2
            pack_data['view_remain_capacity'] = pack_remain_capacity

            # Define number P
            if offset >= len(fields):
                break
            offset += 1

            # Full capacity
            if offset + 1 >= len(fields):
                break
            full_cap_hex = fields[offset] + fields[offset + 1]
            pack_full_capacity = int(full_cap_hex, 16) / 100.0
            offset += 2
            pack_data['view_full_capacity'] = pack_full_capacity

            # Default SOC
            pack_data['view_SOC'] = round(pack_remain_capacity / pack_full_capacity * 100.0, 1) if pack_full_capacity > 0 else 0.0

            # Cycle count
            if offset + 1 >= len(fields):
                break
            cycle_hex = fields[offset] + fields[offset + 1]
            cycle_number = int(cycle_hex, 16)
            offset += 2
            pack_data['view_cycle_number'] = cycle_number

            # Design capacity
            if offset + 1 >= len(fields):
                break
            design_cap_hex = fields[offset] + fields[offset + 1]
            pack_design_capacity = int(design_cap_hex, 16) / 100.0
            offset += 2
            pack_data['view_design_capacity'] = pack_design_capacity

            # SOC percent (1 byte)
            if offset < len(fields):
                soc_percent = int(fields[offset], 16)
                offset += 1
                pack_data['view_SOC'] = round(float(soc_percent), 1)

            # Skip Accumulated Charge Capacity (4 bytes)
            if offset + 3 < len(fields):
                offset += 4

            # Skip Accumulated Discharge Capacity (4 bytes)
            if offset + 3 < len(fields):
                offset += 4

            # SOH (1 byte)
            if offset < len(fields):
                soh_percent = int(fields[offset], 16)
                offset += 1
                pack_data['view_SOH'] = round(float(soh_percent), 1)
            else:
                pack_data['view_SOH'] = round(pack_full_capacity / pack_design_capacity * 100.0, 0) if pack_design_capacity > 0 else 100.0

            # Skip Vbat (2 bytes)
            if offset + 1 < len(fields):
                offset += 2

            # Skip Independent Current (2 bytes)
            if offset + 1 < len(fields):
                offset += 2

            packs_data.append(pack_data)

        return packs_data

    def parse_warning_data_wifi(self, fields):
        """Parse warning data fields according to PCLVBattery / dataParser.js format."""
        try:
            pack_count = int(fields[7], 16)
            if pack_count <= 0:
                pack_count = 1
        except Exception:
            pack_count = 1

        offset = 8
        packs_data = []

        for pack_idx in range(pack_count):
            if offset >= len(fields):
                break

            pack = {}

            # 1. Cell number
            try:
                cell_number = int(fields[offset], 16)
            except Exception:
                cell_number = 0
            pack['cell_number'] = cell_number
            offset += 1

            # 2. Cell voltage warnings
            cell_voltage_warnings = []
            for _ in range(cell_number):
                if offset >= len(fields):
                    break
                val = int(fields[offset], 16)
                cell_voltage_warnings.append(self.interpret_warning(val))
                offset += 1
            pack['cell_voltage_warnings'] = cell_voltage_warnings

            # 3. Temperature sensor number
            if offset >= len(fields):
                break
            try:
                temp_sensor_number = int(fields[offset], 16)
            except Exception:
                temp_sensor_number = 0
            pack['temp_sensor_number'] = temp_sensor_number
            offset += 1

            # 4. Temperature sensor warnings
            temp_sensor_warnings = []
            for _ in range(temp_sensor_number):
                if offset >= len(fields):
                    break
                val = int(fields[offset], 16)
                temp_sensor_warnings.append(self.interpret_warning(val))
                offset += 1
            pack['temp_sensor_warnings'] = temp_sensor_warnings

            # 5. Pack charge current warning
            if offset < len(fields):
                pack['warn_charge_current'] = self.interpret_warning(int(fields[offset], 16))
                offset += 1

            # 6. Pack total voltage warning
            if offset < len(fields):
                pack['warn_total_voltage'] = self.interpret_warning(int(fields[offset], 16))
                offset += 1

            # 7. Pack discharge current warning
            if offset < len(fields):
                pack['warn_discharge_current'] = self.interpret_warning(int(fields[offset], 16))
                offset += 1

            # 8. Protect State 1
            if offset < len(fields):
                val = int(fields[offset], 16)
                pack['protect_state_1'] = {
                    'protect_short_circuit': bool(val & 0b01000000),
                    'protect_high_discharge_current': bool(val & 0b00100000),
                    'protect_high_charge_current': bool(val & 0b00010000),
                    'protect_low_total_voltage': bool(val & 0b00001000),
                    'protect_high_total_voltage': bool(val & 0b00000100),
                    'protect_low_cell_voltage': bool(val & 0b00000010),
                    'protect_high_cell_voltage': bool(val & 0b00000001),
                }
                offset += 1

            # 9. Protect State 2 (using PCLVBattery.js mapping)
            if offset < len(fields):
                val = int(fields[offset], 16)
                pack['protect_state_2'] = {
                    'status_fully_charged': bool(val & 0b10000000),
                    'protect_high_MOS_temp': bool(val & 0b01000000),
                    'protect_low_env_temp': bool(val & 0b00100000),
                    'protect_high_env_temp': bool(val & 0b00010000),
                    'protect_low_discharge_temp': bool(val & 0b00001000),
                    'protect_low_charge_temp': bool(val & 0b00000100),
                    'protect_high_discharge_temp': bool(val & 0b00000010),
                    'protect_high_charge_temp': bool(val & 0b00000001),
                }
                offset += 1

            # 10. Instruction State
            if offset < len(fields):
                val = int(fields[offset], 16)
                pack['instruction_state'] = {
                    'status_heating': bool(val & 0b10000000),
                    'status_charger_avaliable': bool(val & 0b00100000),
                    'status_reverse_connected': bool(val & 0b00010000),
                    'status_discharge_enabled': bool(val & 0b00000100),
                    'status_charge_enabled': bool(val & 0b00000010),
                    'status_current_limit_enabled': bool(val & 0b00000001),
                }
                offset += 1

            # 11. Control State
            if offset < len(fields):
                val = int(fields[offset], 16)
                pack['control_state'] = {
                    'led_warn_function': bool(val & 0b00100000),
                    'current_limit_function': bool(val & 0b00010000),
                    'current_limit_gear': bool(val & 0b00001000),
                    'buzzer_warn_function': bool(val & 0b00000001),
                }
                offset += 1

            # 12. Fault State (using PCLVBattery.js mapping)
            if offset < len(fields):
                val = int(fields[offset], 16)
                pack['fault_state'] = {
                    'fault_sampling': bool(val & 0b00010000),
                    'fault_cell': bool(val & 0b00001000),
                    'fault_NTC': bool(val & 0b00000100),
                    'fault_discharge_MOS': bool(val & 0b00000010),
                    'fault_charge_MOS': bool(val & 0b00000001),
                }
                offset += 1

            # 13. balance_state_1
            if offset < len(fields):
                pack['balance_state_1'] = int(fields[offset], 16)
                offset += 1

            # 14. balance_state_2
            if offset < len(fields):
                pack['balance_state_2'] = int(fields[offset], 16)
                offset += 1

            # 15. Warn State 1
            if offset < len(fields):
                val = int(fields[offset], 16)
                pack['warn_state_1'] = {
                    'warn_high_discharge_current': bool(val & 0b00100000),
                    'warn_high_charge_current': bool(val & 0b00010000),
                    'warn_low_total_voltage': bool(val & 0b00001000),
                    'warn_high_total_voltage': bool(val & 0b00000100),
                    'warn_low_cell_voltage': bool(val & 0b00000010),
                    'warn_high_cell_voltage': bool(val & 0b00000001),
                }
                offset += 1

            # 16. Warn State 2
            if offset < len(fields):
                val = int(fields[offset], 16)
                pack['warn_state_2'] = {
                    'warn_low_SOC': bool(val & 0b10000000),
                    'warn_high_MOS_temp': bool(val & 0b01000000),
                    'warn_low_env_temp': bool(val & 0b00100000),
                    'warn_high_env_temp': bool(val & 0b00010000),
                    'warn_low_discharge_temp': bool(val & 0b00001000),
                    'warn_low_charge_temp': bool(val & 0b00000100),
                    'warn_high_discharge_temp': bool(val & 0b00000010),
                    'warn_high_charge_temp': bool(val & 0b00000001),
                }
                offset += 1

            # Skip ErrStates2
            if offset < len(fields):
                offset += 1
            # Skip ProtectStates3
            if offset < len(fields):
                offset += 1
            # Skip ActiveEqualisationStates1
            if offset < len(fields):
                offset += 1
            # Skip ActiveEqualisationStates2
            if offset < len(fields):
                offset += 1
            # Skip ErrStates3
            if offset < len(fields):
                offset += 1

            packs_data.append(pack)

        return packs_data

    def get_analog_data(self, pack_number=None):
        """Passively read frames and return the latest analog telemetry."""
        if self.latest_analog_data is not None:
            data = self.latest_analog_data
            self.latest_analog_data = None
            return data

        start_time = time.time()
        timeout = self.data_refresh_interval
        while time.time() - start_time < timeout:
            self.process_incoming_data(timeout=1.0)
            if self.latest_analog_data is not None:
                data = self.latest_analog_data
                self.latest_analog_data = None
                return data
            time.sleep(0.1)
        return None

    def get_warning_data(self, pack_number=None):
        """Passively read frames and return the latest warning telemetry."""
        if self.latest_warning_data is not None:
            data = self.latest_warning_data
            self.latest_warning_data = None
            return data

        start_time = time.time()
        timeout = self.data_refresh_interval
        while time.time() - start_time < timeout:
            self.process_incoming_data(timeout=1.0)
            if self.latest_warning_data is not None:
                data = self.latest_warning_data
                self.latest_warning_data = None
                return data
            time.sleep(0.1)
        return None

    def publish_analog_data_mqtt(self, pack_number=None):
        """Publish analog data to MQTT."""
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
            'view_power': 'power',
            'view_energy_charged': 'energy',
            'view_energy_discharged': 'energy',
            'view_SOH': 'null',
            'view_SOC': 'null',
            'random_number': 'null',
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
            'view_power': 'measurement',
            'view_energy_charged': 'total',
            'view_energy_discharged': 'total',
            'view_SOH': 'measurement',
            'view_SOC': 'measurement',
            'random_number': 'measurement',
        }

        analog_data = self.get_analog_data(pack_number)
        if analog_data is None:
            return None

        total_packs_num = len(analog_data)
        if total_packs_num < 1:
            self.logger.error("No packs found")
            return None

        self.ha_comm.publish_sensor_state(total_packs_num, 'packs', "total_packs_num")
        self.ha_comm.publish_sensor_discovery("total_packs_num", "packs", icons['total_packs_num'], deviceclasses['total_packs_num'], stateclasses['total_packs_num'])

        total_full_capacity = round(sum(d.get('view_full_capacity', 0.0) for d in analog_data), 2)
        self.ha_comm.publish_sensor_state(total_full_capacity, 'Ah', "total_full_capacity")
        self.ha_comm.publish_sensor_discovery("total_full_capacity", "Ah", icons['total_full_capacity'], deviceclasses['total_full_capacity'], stateclasses['total_full_capacity'])

        total_remain_capacity = round(sum(d.get('view_remain_capacity', 0.0) for d in analog_data), 2)
        self.ha_comm.publish_sensor_state(total_remain_capacity, 'Ah', "total_remain_capacity")
        self.ha_comm.publish_sensor_discovery("total_remain_capacity", "Ah", icons['total_remain_capacity'], deviceclasses['total_remain_capacity'], stateclasses['total_remain_capacity'])

        total_current = round(sum(d.get('view_current', 0.0) for d in analog_data), 2)
        self.ha_comm.publish_sensor_state(total_current, 'A', "total_current")
        self.ha_comm.publish_sensor_discovery("total_current", "A", icons['total_current'], deviceclasses['total_current'], stateclasses['total_current'])

        total_soc = round(total_remain_capacity / total_full_capacity * 100.0, 1) if total_full_capacity > 0 else 0.0
        self.ha_comm.publish_sensor_state(total_soc, '%', "total_SOC")
        self.ha_comm.publish_sensor_discovery("total_SOC", "%", icons['total_SOC'], deviceclasses['total_SOC'], stateclasses['total_SOC'])

        total_soh = round(sum(d.get('view_SOH', 0.0) for d in analog_data) / total_packs_num, 1)
        self.ha_comm.publish_sensor_state(total_soh, '%', "total_SOH")
        self.ha_comm.publish_sensor_discovery("total_SOH", "%", icons['total_SOH'], deviceclasses['total_SOH'], stateclasses['total_SOH'])

        total_voltage = round(sum(d.get('view_voltage', 0.0) for d in analog_data) / total_packs_num, 2)
        self.ha_comm.publish_sensor_state(total_voltage, 'V', "total_voltage")
        self.ha_comm.publish_sensor_discovery("total_voltage", "V", icons['total_voltage'], deviceclasses['total_voltage'], stateclasses['total_voltage'])

        total_power = round(sum(d.get('view_power', 0.0) for d in analog_data), 1)
        self.ha_comm.publish_sensor_state(total_power, 'kW', "total_power")
        self.ha_comm.publish_sensor_discovery("total_power", "kW", icons['total_power'], deviceclasses['total_power'], stateclasses['total_power'])

        total_energy_charged, total_energy_discharged = self.calculate_cumulative_energy(total_power)
        self.ha_comm.publish_sensor_state(total_energy_charged, 'Wh', "total_energy_charged")
        self.ha_comm.publish_sensor_discovery("total_energy_charged", "Wh", icons['total_energy_charged'], deviceclasses['total_energy_charged'], stateclasses['total_energy_charged'])

        self.ha_comm.publish_sensor_state(total_energy_discharged, 'Wh', "total_energy_discharged")
        self.ha_comm.publish_sensor_discovery("total_energy_discharged", "Wh", icons['total_energy_discharged'], deviceclasses['total_energy_discharged'], stateclasses['total_energy_discharged'])

        all_cell_voltages = [voltage for d in analog_data for voltage in d.get('cell_voltages', [])]

        total_cell_voltage_max = max(all_cell_voltages) if all_cell_voltages else None
        self.ha_comm.publish_sensor_state(total_cell_voltage_max, 'mV', "total_cell_voltage_max")
        self.ha_comm.publish_sensor_discovery("total_cell_voltage_max", "mV", icons['total_cell_voltage_max'], deviceclasses['total_cell_voltage_max'], stateclasses['total_cell_voltage_max'])

        total_cell_voltage_min = min(all_cell_voltages) if all_cell_voltages else None
        self.ha_comm.publish_sensor_state(total_cell_voltage_min, 'mV', "total_cell_voltage_min")
        self.ha_comm.publish_sensor_discovery("total_cell_voltage_min", "mV", icons['total_cell_voltage_min'], deviceclasses['total_cell_voltage_min'], stateclasses['total_cell_voltage_min'])

        if total_cell_voltage_max is not None and total_cell_voltage_min is not None:
            total_cell_voltage_diff = total_cell_voltage_max - total_cell_voltage_min
            self.ha_comm.publish_sensor_state(total_cell_voltage_diff, 'mV', "total_cell_voltage_diff")
            self.ha_comm.publish_sensor_discovery("total_cell_voltage_diff", "mV", icons['total_cell_voltage_diff'], deviceclasses['total_cell_voltage_diff'], stateclasses['total_cell_voltage_diff'])

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
                    self.ha_comm.publish_sensor_state(value, unit, f"pack_{pack_i:02}_{key}")
                    self.ha_comm.publish_sensor_discovery(f"pack_{pack_i:02}_{key}", unit, icon, deviceclass, stateclass)

    def publish_warning_data_mqtt(self, pack_number=None):
        """Publish warning data to MQTT."""
        warn_data = self.get_warning_data(pack_number)
        if warn_data is None:
            return None

        total_packs_num = len(warn_data)
        if total_packs_num < 1:
            self.logger.error("No packs found for warning info")
            return None

        pack_i = 0
        for pack in warn_data:
            pack_i += 1
            self.logger.debug(f"Publishing warnings for pack {pack_i}")
            for key, value in pack.items():
                if key == 'cell_voltage_warnings':
                    cell_i = 0
                    icon = "mdi:battery-heart-variant"
                    for cell_voltage_warning in value:
                        cell_i += 1
                        self.ha_comm.publish_warn_state(cell_voltage_warning, f"pack_{pack_i:02}_cell_voltage_warning_{cell_i:02}")
                        self.ha_comm.publish_warn_discovery(f"pack_{pack_i:02}_cell_voltage_warning_{cell_i:02}", icon)
                elif key == 'temp_sensor_warnings':
                    temp_i = 0
                    icon = "mdi:battery-heart-variant"
                    for temp_sensor_warning in value:
                        temp_i += 1
                        self.ha_comm.publish_warn_state(temp_sensor_warning, f"pack_{pack_i:02}_temperature_warning_{temp_i:02}")
                        self.ha_comm.publish_warn_discovery(f"pack_{pack_i:02}_temperature_warning_{temp_i:02}", icon)
                elif key in ['protect_state_1', 'protect_state_2', 'instruction_state', 'fault_state', 'warn_state_1', 'warn_state_2']:
                    icon = "mdi:battery-alert" if "protect" in key or "warn" in key else "mdi:battery-check"
                    if key == 'fault_state':
                        icon = "mdi:alert"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}", icon)
                elif key not in ['cell_number', 'temp_sensor_number', 'control_state', 'balance_state_1', 'balance_state_2']:
                    icon = "mdi:battery-heart-variant"
                    self.ha_comm.publish_warn_state(value, f"pack_{pack_i:02}_{key}")
                    self.ha_comm.publish_warn_discovery(f"pack_{pack_i:02}_{key}", icon)
