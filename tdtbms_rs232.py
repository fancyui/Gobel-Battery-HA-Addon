import struct
import logging

class TDTBMS232:

    def __init__(self, bms_comm, ha_comm, data_refresh_interval, debug, if_random):
        self.bms_comm = bms_comm
        self.ha_comm = ha_comm
        self.data_refresh_interval = data_refresh_interval
        self.if_random = if_random

        # Configure logging
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def lchksum_calc(self, lenid):
        try:
            chksum = sum(int(chr(lenid[element]), 16) for element in range(len(lenid))) % 16
            chksum_bin = '{0:04b}'.format(chksum)
            flip_bits = ''.join('1' if b == '0' else '0' for b in chksum_bin)
            chksum = (int(flip_bits, 2) + 1) % 16
            return format(chksum, 'X')
        except Exception as e:
            self.logger.error(f"Error calculating LCHKSUM using LENID: {lenid}")
            self.logger.error(f"Error details: {str(e)}")
            return False
    
    def chksum_calc(self, data):
        try:
            chksum = sum(data[element] for element in range(1, len(data))) % 65536
            chksum_bin = '{0:016b}'.format(chksum)
            flip_bits = ''.join('1' if b == '0' else '0' for b in chksum_bin)
            chksum = format(int(flip_bits, 2) + 1, 'X')
            return chksum
        except Exception as e:
            self.logger.error(f"Error calculating CHKSUM using data: {data}")
            self.logger.error(f"Error details: {str(e)}")
            return False
    
    def hex_to_signed(self, hex_str):
        """
        Convert a 16-bit hexadecimal string to signed integer value.
        
        :param hex_str: Hexadecimal string representing battery current (e.g., "FFFB")
        :return: Signed integer current value
        """
        # Convert the hexadecimal string to an integer
        raw_value = int(hex_str, 16)
        
        # Process the 16-bit two's complement signed integer
        if raw_value & 0x8000:  # Check the sign bit (if the highest bit is 1)
            # Handle negative numbers: invert bits and add 1, then attach negative sign
            signed_value = -((~raw_value & 0xFFFF) + 1)
        else:
            signed_value = raw_value
        
        
        return signed_value


    def generate_bms_request(self, command, pack_number=None):
        commands_table = {
            'pack_number': b"\x39\x30",
            'analog': b"\x34\x32",
            'software_version': b"\x43\x31",
            'product_info': b"\x43\x32",
            'capacity': b"\x41\x36",
            'warning_info': b"\x34\x34",
            'get_time': b"\x42\x31",
            'pack_quantity': b"\x39\x30",
        }
        
        lenids_table = {
            'pack_number': b"000",
            'analog': b"002",
            'software_version': b"000",
            'product_info': b"000",
            'capacity': b"000",
            'warning_info': b"002",
            'get_time': b"000",
            'pack_quantity': b"000",
        }
    
        if command not in commands_table:
            raise ValueError("Invalid command")
    
        ver = b"\x32\x35"
        cid1 = b"\x34\x36"
        cid2 = commands_table[command]
        
        pack_number = pack_number if pack_number is not None else 255
    
        info = f"{pack_number:02X}".encode('ascii')

        adr = info
        
        request = b'\x7e' + ver + adr + cid1 + cid2
        
        LENID =  lenids_table[command]
        
        LCHKSUM = self.lchksum_calc(LENID)
    
        if LCHKSUM is False:
            return None
    
        if LENID == b"000":
            request += LCHKSUM.encode('ascii') + LENID
        else:
            request += LCHKSUM.encode('ascii') + LENID + info
        
        CHKSUM = self.chksum_calc(request)
        if CHKSUM is False:
            return None
    
        request += CHKSUM.encode('ascii') + b'\x0d'
    
        return request
    
    
    
    
    
    def generate_mosfet_control_request(self, command_type, state):
        """
        Generates a request to send to the BMS to control MOSFET states.
        
        Parameters:
        command_type (str): The type of MOSFET control command to send to the BMS.
                            It can be one of the following:
                            - 'charge' for controlling charge MOSFET.
                            - 'discharge' for controlling discharge MOSFET.
        state (int): The state to set for the MOSFET (0 to open, 1 to close).
        
        Returns:
        bytes: The request message to be sent to the BMS.
        """
        
        SOI = 0x7E
        VER = 0x32
        ADR = 0x35
        EOI = 0x0D
        
        commands = {
            'charge': (0x46, 0x9A, 0x02),
            'discharge': (0x46, 0x9B, 0x02)
        }
        
        if command_type not in commands:
            raise ValueError("Invalid command type")
        
        if state not in [0, 1]:
            raise ValueError("Invalid state. Must be 0 (open) or 1 (close)")
        
        CID1, CID2, length = commands[command_type]
        data_info = struct.pack('B', state)
        
        len_id = struct.pack('B', length)
        data = struct.pack('BBBBBB', SOI, VER, ADR, CID1, CID2, length) + data_info + struct.pack('BB', EOI)
        chk_sum = calculate_checksum(data)
        
        request = data[:-1] + struct.pack('B', chk_sum) + data[-1:]
        return request
    
    
    
    
    
    
    
    def parse_analog_data(self, response, pack_number):
        """
        Parses the ASCII response string to extract pack analog data for multiple packs.
    
        Args:
        response (str): The ASCII response string from the BMS.
    
        Returns:
        list: Parsed data containing pack analog information for each pack.
        """
        packs_data = []
    
        # Ignore the first character if it is '~'
        if response[0] == '~':
            response = response[1:]
    
        # Split the response into fields (assuming each field is 2 characters representing a byte)
        fields = [response[i:i + 2] for i in range(0, len(response), 2)]
    
        # Debug: Print the fields to verify their contents
        self.logger.debug(f"fields: {fields}")
        # Check the command and response validity
        if fields[2] != '46' or fields[3] != '00':
            raise ValueError(f"Invalid command or response code: {fields[2]} {fields[3]}")
            return None
    
        # Extract the length of the data information
        length = int(fields[4] + fields[5], 16)
    
        # Start parsing the data information
        offset = 6  # Start after fixed header fields
    
        # INFOFLAG
        infoflag = int(fields[offset], 16)
        offset += 1
    
        # Number of packs
        num_packs = int(fields[offset], 16)
        offset += 1

        if num_packs != pack_number:
            raise ValueError(f"Invalid data")
            return None
    
        # for pack_index in range(num_packs):
        pack_data = {}

        # Number of cells
        num_cells = int(fields[offset], 16)
        offset += 1
        pack_data['view_num_cells'] = num_cells

        # Cell voltages
        cell_voltages = []
        for cell_index in range(num_cells):
            voltage = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for voltage
            cell_voltages.append(voltage)
            offset += 2
        pack_data['cell_voltages'] = cell_voltages

        cell_voltage_max = max(cell_voltages)
        cell_voltage_min = min(cell_voltages)

        pack_data['cell_voltage_max'] = cell_voltage_max
        pack_data['cell_voltage_min'] = cell_voltage_min

        # Number of temperature sensors
        num_temps = int(fields[offset], 16)
        offset += 1
        pack_data['view_num_temps'] = num_temps

        # Temperatures
        temperatures = []
        for temp_index in range(num_temps):
            temperature = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for temperature
            temperature = round(temperature / 10 - 273.15, 2)  # Convert tenths of degrees Kelvin to degrees Celsius
            temperatures.append(temperature)
            offset += 2
        pack_data['temperatures'] = temperatures

        # Pack current
        pack_current = fields[offset] + fields[offset + 1]  # Combine two bytes for current
        pack_current = self.hex_to_signed(pack_current) / 100

        offset += 2
        
        pack_data['view_current'] = pack_current

        # Pack total voltage
        pack_total_voltage = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for total voltage
        pack_total_voltage = round(pack_total_voltage / 1000, 2)  # Convert mV to V
        offset += 2
        pack_data['view_voltage'] = pack_total_voltage

        pack_power = round(pack_total_voltage * pack_current / 1000, 4) # Convert W to kW
        pack_data['view_power'] = pack_power

        pack_data['view_energy_charged'] = pack_power * self.data_refresh_interval / 3600 * 1000 if pack_power >= 0 else 0
        pack_data['view_energy_discharged'] = abs(pack_power) * self.data_refresh_interval / 3600 * 1000 if pack_power < 0 else 0

        # Pack remain capacity
        pack_remain_capacity = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for remaining capacity
        pack_remain_capacity = round(pack_remain_capacity / 100, 2)  # Convert 10mAH to AH
        offset += 2
        pack_data['view_remain_capacity'] = pack_remain_capacity

        # Define number P
        define_number_p = int(fields[offset], 16)
        offset += 1

        # Pack full capacity
        pack_full_capacity = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for full capacity
        pack_full_capacity = round(pack_full_capacity / 100, 2)  # Convert 10mAH to AH
        offset += 2
        pack_data['view_full_capacity'] = pack_full_capacity

        pack_data['view_SOC'] = round(pack_remain_capacity / pack_full_capacity * 100, 1)

        # Cycle number
        cycle_number = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for cycle number
        offset += 2
        pack_data['view_cycle_number'] = cycle_number

        # Pack design capacity
        pack_design_capacity = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for design capacity
        pack_design_capacity = round(pack_design_capacity / 100, 2)  # Convert 10mAH to AH
        offset += 2
        pack_data['view_design_capacity'] = pack_design_capacity

        pack_data['view_SOH'] = round(pack_full_capacity / pack_design_capacity * 100, 0)

        # packs_data.append(pack_data)
    
        return pack_data
    
    
    
    
    def extract_warnstate(self, data, pack_number):
        # Ensure the data starts with the SOI character (~)
        if data[0] != '~':
            raise ValueError("Data does not start with SOI (~)")
    
        # Remove SOI (~)
        data = data[1:]
        
        # Extract relevant positions
        ver = data[0:2]
        adr = data[2:4]
        command = data[4:6]
        rtn = data[6:8]
        length_high_byte = data[8:10]
        length_low_byte = data[10:12]
        num_pack = data[14:16]

        if int(num_pack, 16) != pack_number:
            raise ValueError(f"Invalid data")
            return None

        # Check the command and response validity
        if command != '46' or rtn != '00':
            raise ValueError(f"Invalid command or response code: {command} {rtn}")
            return None
        
        # Calculate LENGTH in bytes
        length = int(length_high_byte + length_low_byte, 16)
        
        # DATAINFO starts after LENGTH field (6th byte position)
        data_start_position = 12
        data_end_position = data_start_position + length * 2
        
        # Extract DATAINFO
        datainfo = data[data_start_position:data_end_position]
        
        # Extract INFOFLAG and WARNSTATE from DATAINFO
        INFOFLAG = datainfo[0:2]
        WARNSTATE = datainfo[2:]  # Remaining part is WARNSTATE
        
        return INFOFLAG, WARNSTATE
    
    # Interpret function for warnings
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
    
    def parse_warnstate(self, warnstate):
        if warnstate == None:
            return None
        warnstate_bytes = bytes.fromhex(warnstate)
        index = 0
    
        # Get PACKnumber
        pack_number = warnstate_bytes[index]
        index += 1
    
        packs_info = []
    
        # for _ in range(pack_number):
        pack_info = {}

        # Parse 1. Cell number
        cell_number = warnstate_bytes[index]
        pack_info['cell_number'] = cell_number
        index += 1

        # Parse 2. Cell voltage warnings
        cell_voltage_warnings = []
        for _ in range(cell_number):
            cell_voltage_warn = warnstate_bytes[index]
            cell_voltage_warnings.append(self.interpret_warning(cell_voltage_warn))
            index += 1
        pack_info['cell_voltage_warnings'] = cell_voltage_warnings

        # Parse 3. Temperature sensor number
        temp_sensor_number = warnstate_bytes[index]
        pack_info['temp_sensor_number'] = temp_sensor_number
        index += 1

        # Parse 4. Temperature sensor warnings
        temp_sensor_warnings = []
        for _ in range(temp_sensor_number):
            temp_sensor_warn = warnstate_bytes[index]
            temp_sensor_warnings.append(self.interpret_warning(temp_sensor_warn))
            index += 1
        pack_info['temp_sensor_warnings'] = temp_sensor_warnings

        # Parse 5. PACK charge current warning
        pack_info['warn_charge_current'] = self.interpret_warning(warnstate_bytes[index])
        index += 1

        # Parse 6. PACK total voltage warning
        pack_info['warn_total_voltage'] = self.interpret_warning(warnstate_bytes[index])
        index += 1

        # Parse 7. PACK discharge current warning
        pack_info['warn_discharge_current'] = self.interpret_warning(warnstate_bytes[index])
        index += 1

        # Detailed interpretation for Protect State 1 based on Char A.19
        protect_state_1 = warnstate_bytes[index]
        pack_info['protect_state_1'] = {
            'protect_short_circuit': bool(protect_state_1 & 0b01000000),
            'protect_high_discharge_current': bool(protect_state_1 & 0b00100000),
            'protect_high_charge_current': bool(protect_state_1 & 0b00010000),
            'protect_low_total_voltage': bool(protect_state_1 & 0b00001000),
            'protect_high_total_voltage': bool(protect_state_1 & 0b00000100),
            'protect_low_cell_voltage': bool(protect_state_1 & 0b00000010),
            'protect_high_cell_voltage': bool(protect_state_1 & 0b00000001),
        }
        index += 1

        # Detailed interpretation for Protect State 2 based on Char A.20
        protect_state_2 = warnstate_bytes[index]
        pack_info['protect_state_2'] = {
            'status_fully_charged': bool(protect_state_2 & 0b10000000),
            'protect_low_env_temp': bool(protect_state_2 & 0b01000000),
            'protect_high_env_temp': bool(protect_state_2 & 0b00100000),
            'protect_high_MOS_temp': bool(protect_state_2 & 0b00010000),
            'protect_low_discharge_temp': bool(protect_state_2 & 0b00001000),
            'protect_low_charge_temp': bool(protect_state_2 & 0b00000100),
            'protect_high_discharge_temp': bool(protect_state_2 & 0b00000010),
            'protect_high_charge_temp': bool(protect_state_2 & 0b00000001),
        }
        index += 1

        instruction_state = warnstate_bytes[index]
        pack_info['instruction_state'] = {
            'status_charger_avaliable': bool(instruction_state & 0b00100000),
            'status_reverse_connected': bool(instruction_state & 0b00010000),
            'status_discharge_enabled': bool(instruction_state & 0b00000100),
            'status_charge_enabled': bool(instruction_state & 0b00000010),
            'status_current_limit_enabled': bool(instruction_state & 0b00000001),
        }
        index += 1
        
        control_state = warnstate_bytes[index]
        pack_info['control_state'] = {
            'led_warn_function': bool(control_state & 0b00100000),
            'current_limit_function': bool(control_state & 0b00010000),
            'current_limit_gear': bool(control_state & 0b00001000),
            'buzzer_warn_function': bool(control_state & 0b00000001),
        }
        index += 1
        
        fault_state = warnstate_bytes[index]
        pack_info['fault_state'] = {
            'fault_sampling': bool(fault_state & 0b00100000),
            'fault_cell': bool(fault_state & 0b00010000),
            'fault_NTC': bool(fault_state & 0b00000100),
            'fault_discharge_MOS': bool(fault_state & 0b00000010),
            'fault_charge_MOS': bool(fault_state & 0b00000001),
        }
        index += 1
        
        pack_info['balance_state_1'] = warnstate_bytes[index]
        index += 1
        
        pack_info['balance_state_2'] = warnstate_bytes[index]
        index += 1


        # Detailed interpretation for Warn State 1 based on Char A.24
        warn_state_1 = warnstate_bytes[index]
        pack_info['warn_state_1'] = {
            'warn_high_discharge_current': bool(warn_state_1 & 0b00100000),
            'warn_high_charge_current': bool(warn_state_1 & 0b00010000),
            'warn_low_total_voltage': bool(warn_state_1 & 0b00001000),
            'warn_high_total_voltage': bool(warn_state_1 & 0b00000100),
            'warn_low_cell_voltage': bool(warn_state_1 & 0b00000010),
            'warn_high_cell_voltage': bool(warn_state_1 & 0b00000001),
        }
        index += 1

        # Detailed interpretation for Warn State 2 based on Char A.25
        warn_state_2 = warnstate_bytes[index]
        pack_info['warn_state_2'] = {
            'warn_low_SOC': bool(warn_state_2 & 0b10000000),
            'warn_high_MOS_temp': bool(warn_state_2 & 0b01000000),
            'warn_low_env_temp': bool(warn_state_2 & 0b00100000),
            'warn_high_env_temp': bool(warn_state_2 & 0b00010000),
            'warn_low_discharge_temp': bool(warn_state_2 & 0b00001000),
            'warn_low_charge_temp': bool(warn_state_2 & 0b00000100),
            'warn_high_discharge_temp': bool(warn_state_2 & 0b00000010),
            'warn_high_charge_temp': bool(warn_state_2 & 0b00000001),
        }
        index += 1

        # packs_info.append(pack_info)
    
        return pack_info
    
    
    
    def parse_warning_data(self, data, pack_number):
        infoflag, warnstate = self.extract_warnstate(data,pack_number)
        pack = self.parse_warnstate(warnstate)
        if pack == None:
            return None
        # packs_data = []
        # for pack in packs_info:
        pack_data = {
            'cell_number': pack['cell_number'],
            'cell_voltage_warnings': pack['cell_voltage_warnings'],
            'temp_sensor_number': pack['temp_sensor_number'],
            'temp_sensor_warnings': pack['temp_sensor_warnings'],
            'warn_charge_current': pack['warn_charge_current'],
            'warn_total_voltage': pack['warn_total_voltage'],
            'warn_discharge_current': pack['warn_discharge_current'],
            'protect_state_1': pack['protect_state_1'],
            'protect_state_2': pack['protect_state_2'],
            'instruction_state': pack['instruction_state'],
            'control_state': pack['control_state'],
            'fault_state': pack['fault_state'],
            'balance_state_1': pack['balance_state_1'],
            'balance_state_2': pack['balance_state_2'],
            'warn_state_1': pack['warn_state_1'],
            'warn_state_2': pack['warn_state_2']
        }
        # packs_data.append(pack_data)
    
        return pack_data
    
    
    
    
    
    def parse_capacity_data(self, data):
        """
        Parses the capacity data received from the BMS.
        
        Parameters:
        data (str): The raw data string received from the BMS.
        
        Returns:
        dict: Parsed capacity information.
        """
        fields = data.split()
        capacity_info = {
            'remaining_capacity': int(fields[0], 16) / 100,  # Assuming the unit is in 0.01 Ah
            'full_charge_capacity': int(fields[1], 16) / 100,  # Assuming the unit is in 0.01 Ah
            'cycle_count': int(fields[2], 16)
        }
        return capacity_info
    
    
    def parse_time_date_data(self, data):
        """
        Parses the time and date data received from the BMS.
        
        Parameters:
        data (str): The raw data string received from the BMS.
        
        Returns:
        dict: Parsed time and date information.
        """
        fields = data.split()
        time_date_info = {
            'year': int(fields[0], 16),
            'month': int(fields[1], 16),
            'day': int(fields[2], 16),
            'hour': int(fields[3], 16),
            'minute': int(fields[4], 16),
            'second': int(fields[5], 16)
        }
        return time_date_info
    
    
    def parse_pack_quantity_data(self, response):
        # Remove the SOI character (~)
        if response.startswith('~'):
            response = response[1:]

        # Extract fields based on the given response structure
        ver = response[0:2]
        adr = response[2:4]
        fixed_hex = response[4:6]
        rtn = response[6:8]
        length = response[8:10]
        lenid = response[10:12]

        # Determine the length of DATAINFO
        if lenid == '02':
            data_info_length = 2  # 2 characters for address confirmation
        else:
            raise ValueError("Invalid LENID value")

        data_info = response[12:14]

        # Convert DATAINFO from hex to integer
        pack_quantity = int(data_info, 16)

        return pack_quantity
    
    
    def parse_software_version_data(self, response):
        # Remove the SOI character (~)
        if response.startswith('~'):
            response = response[1:]

        # Extract fields based on the given response structure
        ver = response[0:2]
        adr = response[2:4]
        fixed_hex = response[4:6]
        rtn = response[6:8]
        length = response[8:10]
        lenid = response[10:12]

        # Determine the length of DATAINFO
        if lenid == '28':
            data_info_length = 20  # 20 characters for software version information
        else:
            raise ValueError("Invalid LENID value")

        data_info = response[12:12 + data_info_length * 2]  # Each character is represented by 2 hex digits

        # Convert DATAINFO from hex to ASCII
        software_version_info = bytes.fromhex(data_info).decode('ascii')

        return software_version_info
    
    
    def parse_product_info_data(self, response):
        # Remove the SOI character (~)
        if response.startswith('~'):
            response = response[1:]

        # Extract fields based on the given response structure
        ver = response[0:2]
        adr = response[2:4]
        fixed_hex = response[4:6]
        rtn = response[6:8]
        length = response[8:10]
        lenid = response[10:12]

        # Determine the length of DATAINFO
        if lenid == '50':
            data_info_length = 40  # 20 characters for BMS and 20 characters for PACK
        elif lenid == '28':
            data_info_length = 20  # 20 characters for BMS only
        else:
            raise ValueError("Invalid LENID value")

        data_info = response[12:12 + data_info_length * 2]  # Each character is represented by 2 hex digits

        # Split DATAINFO into BMS and PACK production information
        bms_info_hex = data_info[:40]  # 20 characters * 2 hex digits
        bms_info = bytes.fromhex(bms_info_hex).decode('ascii')

        if lenid == '50':
            pack_info_hex = data_info[40:80]  # Next 20 characters * 2 hex digits
            pack_info = bytes.fromhex(pack_info_hex).decode('ascii')
        else:
            pack_info = None

        return bms_info, pack_info
    
    
    
    
    def get_analog_data(self, pack_number=None):
        
        try:
            # Generate request
            self.logger.debug(f"Trying to prepare analog request")
            request = self.generate_bms_request("analog",pack_number)
            self.logger.debug(f"analog request: {request}")

            # Send request to BMS
            self.logger.debug(f"Trying to send analog request")
            if not self.bms_comm.send_data(request):
                return None
            self.logger.debug(f"analog request sent")
    
            # Receive response from BMS
            self.logger.debug(f"Trying to receive analog data")
            response = self.bms_comm.receive_data()
            self.logger.debug(f"analog data recieved: {response}")
            if response is None:
                return None
            
            # Parse analog data from response
            self.logger.debug(f"Trying to parse analog data")
            analog_data = self.parse_analog_data(response,pack_number)
            self.logger.debug(f"analog data parsed: {analog_data}")
            return analog_data
    
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None
    
    
    
    def get_warning_data(self, pack_number=None):
        
        try:
            # Generate request
            self.logger.debug(f"Trying to prepare warning request")
            request = self.generate_bms_request("warning_info",pack_number)
            self.logger.debug(f"warning request: {request}")
            
            # Send request to BMS
            self.logger.debug(f"Trying to send warning request")
            if not self.bms_comm.send_data(request):
                return None
            self.logger.debug(f"warning request sent")
            
            # Receive response from BMS
            self.logger.debug(f"Trying to receive warning data")
            response = self.bms_comm.receive_data()
            self.logger.debug(f"warning data recieved: {response}")
            if response is None:
                return None
            
            # Parse analog data from response
            self.logger.debug(f"Trying to parse warning data")
            warning_data = self.parse_warning_data(response,pack_number)
            self.logger.debug(f"warning data parsed: {warning_data}")
    
            return warning_data
    
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None
    
    
    
    def get_capacity_data(bms_connection, pack_number=None):
        
        try:
            # Generate request
            self.logger.debug(f"Trying to prepare capacity request")
            request = self.generate_bms_request("capacity",pack_number)
            self.logger.debug(f"capacity request: {request}")

            # Send request to BMS
            self.logger.debug(f"Trying to send capacity request")
            if not self.bms_comm.send_data(request):
                return None
            self.logger.debug(f"capacity request sent")
    
            # Receive response from BMS
            self.logger.debug(f"Trying to receive capacity data")
            response = self.bms_comm.receive_data()
            self.logger.debug(f"capacity data recieved: {response}")
            if response is None:
                return None
            
            # Parse analog data from response
            self.logger.debug(f"Trying to parse capacity data")
            capacity_data = self.parse_capacity_data(response)
            self.logger.debug(f"capacity data parsed: {capacity_data}")
            return capacity_data
    
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None
    
    
    
    def get_product_info_data(bms_connection, pack_number=None):
        
        try:
            # Generate request
            self.logger.debug(f"Trying to prepare product info request")
            request = self.generate_bms_request("product_info",pack_number)
            self.logger.debug(f"product info request: {request}")

            # Send request to BMS
            self.logger.debug(f"Trying to send product info request")
            if not self.bms_comm.send_data(request):
                return None
            self.logger.debug(f"product info request sent")
    
            # Receive response from BMS
            self.logger.debug(f"Trying to receive product info data")
            response = self.bms_comm.receive_data()
            self.logger.debug(f"product info data recieved: {response}")
            if response is None:
                return None
            
            # Parse analog data from response
            self.logger.debug(f"Trying to parse product info data")
            bms_info, pack_info =  self.parse_product_info_data(response)
            self.logger.debug(f"product info data parsed: {bms_info}")
            self.logger.debug(f"product info data parsed: {pack_info}")
            return bms_info, pack_info
    
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    def get_pack_quantity_data(self, pack_number=None):
        
        
        try:
            # Generate request
            self.logger.debug(f"Trying to prepare pack quantity request")
            request = self.generate_bms_request("pack_quantity",pack_number)
            self.logger.debug(f"pack quantity request: {request}")

            # Send request to BMS
            self.logger.debug(f"Trying to send pack quantity request")
            if not self.bms_comm.send_data(request):
                return None
            self.logger.debug(f"pack quantity request sent")
    
            # Receive response from BMS
            self.logger.debug(f"Trying to receive pack quantity data")
            response = self.bms_comm.receive_data()
            self.logger.debug(f"pack quantity data recieved: {response}")
            if response is None:
                return None
            
            # Parse analog data from response
            self.logger.debug(f"Trying to parse pack quantity data")
            pack_quantity_data = self.parse_pack_quantity_data(response)
            self.logger.debug(f"pack quantity data parsed: {pack_quantity_data}")
            return pack_quantity_data
    
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    def check_if_pack_exsit(self, pack_number):
        try:
            pack_num_data = self.get_pack_num_data(pack_number)
            if int(pack_num_data) == pack_number:
                if_exsit = pack_number
            else:
                if_exsit = False

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    def publish_analog_data_api(self, pack_number=None):

        units = {
            'num_cells': 'cells',
            'cell_voltages': 'mV',
            'num_temps': 'NTCs',
            'temperatures': '℃',
            'pack_current': 'A',
            'pack_total_voltage': 'V',
            'pack_remain_capacity': 'Ah',
            'pack_full_capacity': 'Ah',
            'cycle_number': 'cycles',
            'pack_design_capacity': 'Ah',
        }

        analog_data = self.get_analog_data(pack_number)

        total_packs_num = len(analog_data)
        self.ha_comm.publish_data(total_packs_num, 'packs', f"{self.base_topic}.total_packs_num")

        total_pack_full_capacity = round(sum(d.get('pack_full_capacity', 0) for d in analog_data),2)
        self.ha_comm.publish_data(total_pack_full_capacity, 'Ah', f"{self.base_topic}.total_pack_full_capacity")

        total_pack_remain_capacity = round(sum(d.get('pack_remain_capacity', 0) for d in analog_data),2)
        self.ha_comm.publish_data(total_pack_remain_capacity, 'Ah', f"{self.base_topic}.total_pack_remain_capacity")

        total_pack_current = round(sum(d.get('pack_current', 0) for d in analog_data),2)
        self.ha_comm.publish_data(total_pack_current, 'A', f"{self.base_topic}.total_pack_current")

        total_soc = round(total_pack_remain_capacity / total_pack_full_capacity * 100, 1) 
        self.ha_comm.publish_data(total_soc, '%', f"{self.base_topic}.total_soc")

        total_mean_voltage = round(sum(d.get('pack_total_voltage', 0) for d in analog_data) / total_packs_num, 2)
        self.ha_comm.publish_data(total_mean_voltage, 'V', f"{self.base_topic}.total_mean_voltage")

        total_power = round(sum(d.get('pack_full_capacity', 0) for d in analog_data),2)
        self.ha_comm.publish_data(total_power, 'kW', f"{self.base_topic}.total_power")

        import random
        random_number = random.randint(1, 100)
        self.ha_comm.publish_data(random_number, 'p', f"{self.base_topic}.random")

        pack_i = 0

        for pack in analog_data:
            pack_i = pack_i + 1
            for key, value in pack.items():
                unit = units.get(key, '')
                if key == 'cell_voltages':
                    cell_i = 0
                    for cell_voltage in value:
                        cell_i = cell_i + 1
                        self.ha_comm.publish_data(cell_voltage, unit, f"{self.base_topic}.pack_{pack_i:02}_cell_voltage_{cell_i:02}")
                        
                elif key == 'temperatures':
                    temperature_i = 0
                    for temperature in value:
                        temperature_i = temperature_i + 1
                        self.ha_comm.publish_data(temperature, unit, f"{self.base_topic}.pack_{pack_i:02}_temperature_{temperature_i:02}")
                        
                else:
                    self.ha_comm.publish_data(value, unit, f"{self.base_topic}.pack_{pack_i:02}_{key}")


    def publish_analog_data_mqtt(self, pack_list):

        units = {
            'view_num_cells': 'cells',
            'cell_voltages': 'mV',
            'cell_voltage_max': 'mV',
            'cell_voltage_min': 'mV',
            'view_num_temps': 'NTCs',
            'temperatures': '℃',
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
            'view_num_cells': 'mdi:database',
            'cell_voltages': 'mdi:sine-wave',
            'cell_voltage_max': 'mdi:align-vertical-top',
            'cell_voltage_min': 'mdi:align-vertical-bottom',
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
            'cell_voltages': 'voltage',
            'cell_voltage_max': 'voltage',
            'cell_voltage_min': 'voltage',
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
            'view_num_cells': 'measurement',
            'cell_voltages': 'measurement',
            'cell_voltage_max': 'measurement',
            'cell_voltage_min': 'measurement',
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

        analog_data = []
        for pack_number in pack_list:
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                analog_data_single = self.get_analog_data(pack_number)
                if analog_data_single is not None:
                    break  # got a valid value, break the loop
                retry_count += 1
                self.logger.debug(f"retry {retry_count} to get analog data of pack: {pack_number}")

            if retry_count == max_retries:
                self.logger.error(f"Failed to get analog data of pack: {pack_number} after {max_retries} retries")
            else:
                analog_data.append(analog_data_single)


        total_packs_num = len(analog_data)

        if total_packs_num < 1:
            self.logger.error("No packs found")
            return None


        self.ha_comm.publish_sensor_state(total_packs_num, 'packs', "total_packs_num")
        self.ha_comm.publish_sensor_discovery("total_packs_num", "packs", icons['total_packs_num'], deviceclasses['total_packs_num'], stateclasses['total_packs_num'])

        total_full_capacity = round(sum(d.get('view_full_capacity', 0) for d in analog_data),2)
        self.ha_comm.publish_sensor_state(total_full_capacity, 'Ah', "total_full_capacity")
        self.ha_comm.publish_sensor_discovery("total_full_capacity", "Ah", icons['total_full_capacity'], deviceclasses['total_full_capacity'], stateclasses['total_full_capacity'])

        total_remain_capacity = round(sum(d.get('view_remain_capacity', 0) for d in analog_data),2)
        self.ha_comm.publish_sensor_state(total_remain_capacity, 'Ah', "total_remain_capacity")
        self.ha_comm.publish_sensor_discovery("total_remain_capacity", "Ah", icons['total_remain_capacity'], deviceclasses['total_remain_capacity'], stateclasses['total_remain_capacity'])

        total_current = round(sum(d.get('view_current', 0) for d in analog_data),2)
        self.ha_comm.publish_sensor_state(total_current, 'A', "total_current")
        self.ha_comm.publish_sensor_discovery("total_current", "A", icons['total_current'], deviceclasses['total_current'], stateclasses['total_current'])

        total_soc = round(total_remain_capacity / total_full_capacity * 100, 1) 
        self.ha_comm.publish_sensor_state(total_soc, '%', "total_SOC")
        self.ha_comm.publish_sensor_discovery("total_SOC", "%", icons['total_SOC'], deviceclasses['total_SOC'], stateclasses['total_SOC'])

        total_soh = round(sum(d.get('view_SOH', 0) for d in analog_data) / total_packs_num, 1)
        self.ha_comm.publish_sensor_state(total_soh, '%', "total_SOH")
        self.ha_comm.publish_sensor_discovery("total_SOH", "%", icons['total_SOH'], deviceclasses['total_SOH'], stateclasses['total_SOH'])

        total_voltage = round(sum(d.get('view_voltage', 0) for d in analog_data) / total_packs_num, 2)
        self.ha_comm.publish_sensor_state(total_voltage, 'V', "total_voltage")
        self.ha_comm.publish_sensor_discovery("total_voltage", "V", icons['total_voltage'], deviceclasses['total_voltage'], stateclasses['total_voltage'])

        total_power = round(sum(d.get('view_power', 0) for d in analog_data),1)
        self.ha_comm.publish_sensor_state(total_power, 'kW', "total_power")
        self.ha_comm.publish_sensor_discovery("total_power", "kW", icons['total_power'], deviceclasses['total_power'], stateclasses['total_power'])

        total_energy_charged = total_power * self.data_refresh_interval / 3600 * 1000 if total_power >= 0 else 0
        self.ha_comm.publish_sensor_state(total_energy_charged, 'Wh', "total_energy_charged")
        self.ha_comm.publish_sensor_discovery("total_energy_charged", "Wh", icons['total_energy_charged'], deviceclasses['total_energy_charged'], stateclasses['total_energy_charged'])

        total_energy_discharged = abs(total_power) * self.data_refresh_interval / 3600 * 1000 if total_power < 0 else 0
        self.ha_comm.publish_sensor_state(total_energy_discharged, 'Wh', "total_energy_discharged")
        self.ha_comm.publish_sensor_discovery("total_energy_discharged", "Wh", icons['total_energy_discharged'], deviceclasses['total_energy_discharged'], stateclasses['total_energy_discharged'])

        # Extract all cell_voltages lists and flatten them into a single list
        all_cell_voltages = [voltage for d in analog_data for voltage in d.get('cell_voltages', [])]

        # Find the maximum and min value from the flattened list
        total_cell_voltage_max = max(all_cell_voltages, default=None)
        self.ha_comm.publish_sensor_state(total_cell_voltage_max, 'V', "total_cell_voltage_max")
        self.ha_comm.publish_sensor_discovery("total_cell_voltage_max", "V", icons['total_cell_voltage_max'], deviceclasses['total_cell_voltage_max'], stateclasses['total_cell_voltage_max'])

        total_cell_voltage_min = min(all_cell_voltages, default=None)
        self.ha_comm.publish_sensor_state(total_cell_voltage_min, 'V', "total_cell_voltage_min")
        self.ha_comm.publish_sensor_discovery("total_cell_voltage_min", "V", icons['total_cell_voltage_min'], deviceclasses['total_cell_voltage_min'], stateclasses['total_cell_voltage_min'])


        if self.if_random:
            import random
            random_number = random.randint(1, 100)
            self.ha_comm.publish_sensor_state(random_number, 'A', "random_number")
            self.ha_comm.publish_sensor_discovery("random_number", "A", icons['random_number'], deviceclasses['random_number'], stateclasses['random_number'])


        pack_i = 0

        for pack in analog_data:
            pack_i = pack_i + 1
            for key, value in pack.items():
                unit = units.get(key, '')
                icon = icons.get(key, '')
                deviceclass = deviceclasses.get(key, '')
                stateclass = stateclasses.get(key, '')

                if key == 'cell_voltages':
                    cell_i = 0
                    for cell_voltage in value:
                        cell_i = cell_i + 1
                        self.ha_comm.publish_sensor_state(cell_voltage, unit, f"pack_{pack_i:02}_cell_voltage_{cell_i:02}")
                        self.ha_comm.publish_sensor_discovery(f"pack_{pack_i:02}_cell_voltage_{cell_i:02}", unit, icon,deviceclass,stateclass)
                        
                elif key == 'temperatures':
                    temperature_i = 0
                    for temperature in value:
                        temperature_i = temperature_i + 1
                        self.ha_comm.publish_sensor_state(temperature, unit, f"pack_{pack_i:02}_temperature_{temperature_i:02}")
                        self.ha_comm.publish_sensor_discovery(f"pack_{pack_i:02}_temperature_{temperature_i:02}", unit, icon,deviceclass,stateclass)
                        
                else:
                    self.ha_comm.publish_sensor_state(value, unit, f"pack_{pack_i:02}_{key}")
                    self.ha_comm.publish_sensor_discovery(f"pack_{pack_i:02}_{key}", unit, icon,deviceclass,stateclass)


    def publish_warning_data_mqtt(self, pack_list):

        warn_data = []
        
        for pack_number in pack_list:
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                warn_data_single = self.get_warning_data(pack_number)
                if warn_data_single is not None:
                    break  # got a valid value, break the loop
                retry_count += 1
                self.logger.debug(f"retry {retry_count} to get warning data of pack: {pack_number}")

            if retry_count == max_retries:
                self.logger.error(f"Failed to get warning data of pack: {pack_number} after {max_retries} retries")
            else:
                warn_data.append(warn_data_single)

        total_packs_num = len(warn_data)

        if total_packs_num < 1:
            self.logger.error("No packs found")
            return None

        pack_i = 0

        for pack in warn_data:
            pack_i = pack_i + 1
            self.logger.debug(f"pack_{pack_i:02}: {pack_i}")
            for key, value in pack.items():
                unit = None
                dclass = None
                if key == 'cell_voltage_warnings':
                    cell_i = 0
                    icon = "mdi:battery-heart-variant"
                    for cell_voltage_warning in value:
                        cell_i = cell_i + 1
                        self.ha_comm.publish_warn_state(cell_voltage_warning, f"pack_{pack_i:02}_cell_voltage_warning_{cell_i:02}")
                        self.ha_comm.publish_warn_discovery(f"pack_{pack_i:02}_cell_voltage_warning_{cell_i:02}",icon)
                elif key == 'temp_sensor_warnings':
                    temp_i = 0
                    icon = "mdi:battery-heart-variant"
                    for temp_sensor_warning in value:
                        temp_i = temp_i + 1
                        self.ha_comm.publish_warn_state(temp_sensor_warning, f"pack_{pack_i:02}_temperature_warning_{temp_i:02}")
                        self.ha_comm.publish_warn_discovery(f"pack_{pack_i:02}_temperature_warning_{temp_i:02}",icon)
                elif key == 'protect_state_1':
                    icon = "mdi:battery-alert"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}",icon)
                elif key == 'protect_state_2':
                    icon = "mdi:battery-alert"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}",icon)
                elif key == 'instruction_state':
                    icon = "mdi:battery-check"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}",icon)
                
                elif key == 'fault_state':
                    icon = "mdi:alert"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}",icon)
                elif key == 'warn_state_1':
                    icon = "mdi:battery-heart-variant"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}",icon)
                elif key == 'warn_state_2':
                    icon = "mdi:battery-heart-variant"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}",icon)
                elif key not in ['cell_number', 'temp_sensor_number', 'control_state', 'balance_state_1', 'balance_state_2']:
                    icon = "mdi:battery-heart-variant"
                    self.ha_comm.publish_warn_state(value, f"pack_{pack_i:02}_{key}")
                    self.ha_comm.publish_warn_discovery(f"pack_{pack_i:02}_{key}",icon)





