import struct

class PACEBMS:

    def __init__(self,BMSComm):
        self.BMSComm = BMSComm

    def lchksum_calc(self, lenid):
        try:
            chksum = sum(int(chr(lenid[element]), 16) for element in range(len(lenid))) % 16
            chksum_bin = '{0:04b}'.format(chksum)
            flip_bits = ''.join('1' if b == '0' else '0' for b in chksum_bin)
            chksum = (int(flip_bits, 2) + 1) % 16
            return format(chksum, 'X')
        except Exception as e:
            print(f"Error calculating LCHKSUM using LENID: {lenid}")
            print(f"Error details: {str(e)}")
            return False
    
    def chksum_calc(self, data):
        try:
            chksum = sum(data[element] for element in range(1, len(data))) % 65536
            chksum_bin = '{0:016b}'.format(chksum)
            flip_bits = ''.join('1' if b == '0' else '0' for b in chksum_bin)
            chksum = format(int(flip_bits, 2) + 1, 'X')
            return chksum
        except Exception as e:
            print(f"Error calculating CHKSUM using data: {data}")
            print(f"Error details: {str(e)}")
            return False
    
    
    def generate_bms_request(self, command, pack_number=None):
        commands_table = {
            'pack_number': b"\x39\x30",
            'analog': b"\x34\x32",
            'software_version': b"\x43\x31",
            'product_info': b"\x43\x32",
            'capacity': b"\x41\x36",
            'warning_info': b"\x34\x34",
        }
        
        lenids_table = {
            'pack_number': b"000",
            'analog': b"002",
            'software_version': b"000",
            'product_info': b"000",
            'capacity': b"000",
            'warning_info': b"002",
        }
    
        if command not in commands_table:
            raise ValueError("Invalid command")
    
        ver = b"\x32\x35"
        adr = b"\x30\x30"
        cid1 = b"\x34\x36"
        cid2 = commands_table[command]
        
        pack_number = pack_number if pack_number is not None else 255
    
        info = f"{pack_number:02X}".encode('ascii')
        
        request = b'\x7e' + ver + adr + cid1 + cid2
        
        LENID =  lenids_table[command]
        
        LCHKSUM = lchksum_calc(LENID)
    
        if LCHKSUM is False:
            return None
    
        request += LCHKSUM.encode('ascii') + LENID + info
        
    
        CHKSUM = chksum_calc(request)
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
    
    
    
    
    
    
    
    def parse_analog_data(self, response):
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
        print("Fields:", fields)
    
        # Check the command and response validity
        if fields[2] != '46' or fields[3] != '00':
            raise ValueError(f"Invalid command or response code: {fields[2]} {fields[3]}")
    
        # Extract the length of the data information
        length = int(fields[4] + fields[5], 16)
        print(f"Data length: {length}")
    
        # Start parsing the data information
        offset = 6  # Start after fixed header fields
    
        # INFOFLAG
        infoflag = int(fields[offset], 16)
        print(f"INFOFLAG: {infoflag}")
        offset += 1
    
        # Number of packs
        num_packs = int(fields[offset], 16)
        print(f"Number of packs: {num_packs}")
        offset += 1
    
        for pack_index in range(num_packs):
            pack_data = {}
    
            # Number of cells
            num_cells = int(fields[offset], 16)
            print(f"Pack {pack_index + 1} - Number of cells: {num_cells}")
            offset += 1
            pack_data['num_cells'] = num_cells
    
            # Cell voltages
            cell_voltages = []
            for cell_index in range(num_cells):
                voltage = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for voltage
                print(f"Pack {pack_index + 1} - Cell {cell_index + 1} voltage: {voltage}")
                cell_voltages.append(voltage)
                offset += 2
            pack_data['cell_voltages'] = cell_voltages
    
            # Number of temperature sensors
            num_temps = int(fields[offset], 16)
            print(f"Pack {pack_index + 1} - Number of temperature sensors: {num_temps}")
            offset += 1
            pack_data['num_temps'] = num_temps
    
            # Temperatures
            temperatures = []
            for temp_index in range(num_temps):
                temperature = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for temperature
                temperature = round(temperature / 10 - 273.15, 2)  # Convert tenths of degrees Kelvin to degrees Celsius
                print(f"Pack {pack_index + 1} - Temperature sensor {temp_index + 1} temperature: {temperature}")
                temperatures.append(temperature)
                offset += 2
            pack_data['temperatures'] = temperatures
    
            # Pack current
            pack_current = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for current
            pack_current = round(pack_current / 100, 2)  # Convert 10mA to A
            if pack_current > 32767:
                pack_current -= 65536
            print(f"Pack {pack_index + 1} - Pack current: {pack_current}")
            offset += 2
            pack_data['pack_current'] = pack_current
    
            # Pack total voltage
            pack_total_voltage = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for total voltage
            pack_total_voltage = round(pack_total_voltage / 1000, 2)  # Convert mV to V
            print(f"Pack {pack_index + 1} - Pack total voltage: {pack_total_voltage}")
            offset += 2
            pack_data['pack_total_voltage'] = pack_total_voltage
    
            # Pack remain capacity
            pack_remain_capacity = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for remaining capacity
            pack_remain_capacity = round(pack_remain_capacity / 100, 2)  # Convert 10mAH to AH
            print(f"Pack {pack_index + 1} - Pack remaining capacity: {pack_remain_capacity}")
            offset += 2
            pack_data['pack_remain_capacity'] = pack_remain_capacity
    
            # Define number P
            define_number_p = int(fields[offset], 16)
            print(f"Pack {pack_index + 1} - Define number P: {define_number_p}")
            offset += 1
    
            # Pack full capacity
            pack_full_capacity = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for full capacity
            pack_full_capacity = round(pack_full_capacity / 100, 2)  # Convert 10mAH to AH
            print(f"Pack {pack_index + 1} - Pack full capacity: {pack_full_capacity}")
            offset += 2
            pack_data['pack_full_capacity'] = pack_full_capacity
    
            # Cycle number
            cycle_number = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for cycle number
            print(f"Pack {pack_index + 1} - Cycle number: {cycle_number}")
            offset += 2
            pack_data['cycle_number'] = cycle_number
    
            # Pack design capacity
            pack_design_capacity = int(fields[offset] + fields[offset + 1], 16)  # Combine two bytes for design capacity
            pack_design_capacity = round(pack_design_capacity / 100, 2)  # Convert 10mAH to AH
            print(f"Pack {pack_index + 1} - Pack design capacity: {pack_design_capacity}")
            offset += 2
            pack_data['pack_design_capacity'] = pack_design_capacity
    
            packs_data.append(pack_data)
    
        return packs_data
    
    
    
    
    def extract_warnstate(self, data):
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
        warnstate_bytes = bytes.fromhex(warnstate)
        index = 0
    
        # Get PACKnumber
        pack_number = warnstate_bytes[index]
        index += 1
    
        packs_info = []
    
        for _ in range(pack_number):
            pack_info = {}
    
            # Parse 1. Cell number
            cell_number = warnstate_bytes[index]
            pack_info['cell_number'] = cell_number
            index += 1
    
            # Parse 2. Cell voltage warnings
            cell_voltage_warnings = []
            for _ in range(cell_number):
                cell_voltage_warn = warnstate_bytes[index]
                cell_voltage_warnings.append(interpret_warning(cell_voltage_warn))
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
                temp_sensor_warnings.append(interpret_warning(temp_sensor_warn))
                index += 1
            pack_info['temp_sensor_warnings'] = temp_sensor_warnings
    
            # Parse 5. PACK charge current warning
            pack_info['charge_current_warn'] = interpret_warning(warnstate_bytes[index])
            index += 1
    
            # Parse 6. PACK total voltage warning
            pack_info['total_voltage_warn'] = interpret_warning(warnstate_bytes[index])
            index += 1
    
            # Parse 7. PACK discharge current warning
            pack_info['discharge_current_warn'] = interpret_warning(warnstate_bytes[index])
            index += 1
    
            # Detailed interpretation for Protect State 1 based on Char A.19
            protect_state_1 = warnstate_bytes[index]
            pack_info['protect_state_1'] = {
                'short_circuit_protect': bool(protect_state_1 & 0b01000000),
                'discharge_current_protect': bool(protect_state_1 & 0b00100000),
                'charge_current_protect': bool(protect_state_1 & 0b00010000),
                'lower_total_voltage_protect': bool(protect_state_1 & 0b00001000),
                'above_total_voltage_protect': bool(protect_state_1 & 0b00000100),
                'lower_cell_voltage_protect': bool(protect_state_1 & 0b00000010),
                'above_cell_voltage_protect': bool(protect_state_1 & 0b00000001),
            }
            index += 1
    
            # Detailed interpretation for Protect State 2 based on Char A.20
            protect_state_2 = warnstate_bytes[index]
            pack_info['protect_state_2'] = {
                'fully_protect': bool(protect_state_2 & 0b10000000),
                'lower_env_temperature_protect': bool(protect_state_2 & 0b01000000),
                'above_env_temperature_protect': bool(protect_state_2 & 0b00100000),
                'above_MOS_temperature_protect': bool(protect_state_2 & 0b00010000),
                'lower_discharge_temperature_protect': bool(protect_state_2 & 0b00001000),
                'lower_charge_temperature_protect': bool(protect_state_2 & 0b00000100),
                'above_discharge_temperature_protect': bool(protect_state_2 & 0b00000010),
                'above_charge_temperature_protect': bool(protect_state_2 & 0b00000001),
            }
            index += 1
    
            # Detailed interpretation for Warn State 1 based on Char A.24
            warn_state_1 = warnstate_bytes[index]
            pack_info['warn_state_1'] = {
                'discharge_current_warn': bool(warn_state_1 & 0b00100000),
                'charge_current_warn': bool(warn_state_1 & 0b00010000),
                'lower_total_voltage_warn': bool(warn_state_1 & 0b00001000),
                'above_total_voltage_warn': bool(warn_state_1 & 0b00000100),
                'lower_cell_voltage_warn': bool(warn_state_1 & 0b00000010),
                'above_cell_voltage_warn': bool(warn_state_1 & 0b00000001),
            }
            index += 1
    
            # Detailed interpretation for Warn State 2 based on Char A.25
            warn_state_2 = warnstate_bytes[index]
            pack_info['warn_state_2'] = {
                'low_power_warn': bool(warn_state_2 & 0b10000000),
                'high_MOS_temperature_warn': bool(warn_state_2 & 0b01000000),
                'low_env_temperature_warn': bool(warn_state_2 & 0b00100000),
                'high_env_temperature_warn': bool(warn_state_2 & 0b00010000),
                'low_discharge_temperature_warn': bool(warn_state_2 & 0b00001000),
                'low_charge_temperature_warn': bool(warn_state_2 & 0b00000100),
                'above_discharge_temperature_warn': bool(warn_state_2 & 0b00000010),
                'above_charge_temperature_warn': bool(warn_state_2 & 0b00000001),
            }
            index += 1
    
            packs_info.append(pack_info)
    
        return packs_info
    
    
    
    def parse_warning_data(self, data):
        infoflag, warnstate = extract_warnstate(data)
        packs_info = parse_warnstate(warnstate)
    
        packs_data = []
        for pack in packs_info:
            pack_data = {
                'cell_number': pack['cell_number'],
                'cell_voltage_warnings': pack['cell_voltage_warnings'],
                'temp_sensor_number': pack['temp_sensor_number'],
                'temp_sensor_warnings': pack['temp_sensor_warnings'],
                'charge_current_warn': pack['charge_current_warn'],
                'total_voltage_warn': pack['total_voltage_warn'],
                'discharge_current_warn': pack['discharge_current_warn'],
                'protect_state_1': pack['protect_state_1'],
                'protect_state_2': pack['protect_state_2'],
                'warn_state_1': pack['warn_state_1'],
                'warn_state_2': pack['warn_state_2']
            }
            packs_data.append(pack_data)
    
        return packs_data
    
    
    
    
    
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
    
    
    def parse_pack_number_data(self, data):
        """
        Parses the pack number data received from the BMS.
        
        Parameters:
        data (str): The raw data string received from the BMS.
        
        Returns:
        int: The pack number.
        """
        return int(data.strip(), 16)
    
    
    def parse_software_version_data(self, data):
        """
        Parses the software version data received from the BMS.
        
        Parameters:
        data (str): The raw data string received from the BMS.
        
        Returns:
        str: The software version.
        """
        return data.strip()
    
    
    def parse_product_info_data(self, data):
        """
        Parses the product information data received from the BMS.
        
        Parameters:
        data (str): The raw data string received from the BMS.
        
        Returns:
        dict: Parsed product information.
        """
        fields = data.split()
        product_info = {
            'manufacturer': fields[0],
            'model': fields[1],
            'serial_number': fields[2]
        }
        return product_info
    
    
    
    
    def get_analog_data(self, pack_number=None):
        
        try:
            # Generate request
            print(f"Trying to prepare analog request")
            request = self.generate_bms_request("analog",pack_number)
            print(f"Analog request: {request}")
            
            # Send request to BMS
            print(f"Trying to send analog request")
            if not self.BMSComm.send_data(request):
                return None
            print(f"Analog request sent")
    
            # Receive response from BMS
            print(f"Trying to receive analog data")
            response = self.BMSComm.receive_data()
            if response is None:
                return None
            print(f"Analog data recieved: {response}")
            
            # Parse analog data from response
            print(f"Trying to parse analog data")
            analog_data = self.parse_analog_data(response)
            print(f"Analog data parsed: {analog_data}")
    
            return analog_data
    
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    
    
    def get_warning_data(self, pack_number=None):
        
        try:
            # Generate request
            print(f"Trying to prepare warning request")
            request = self.generate_bms_request("warning_info",pack_number)
            print(f"warning request: {request}")
            
            # Send request to BMS
            print(f"Trying to send analog request")
            if not self.BMSComm.send_data(request):
                return None
            print(f"warning request sent")
            
            # Receive response from BMS
            print(f"Trying to receive warning data")
            response = self.BMSComm.receive_data()
            print(f"warning data recieved: {response}")
            if response is None:
                return None
            
            # Parse analog data from response
            print(f"Trying to parse warning data")
            warning_data = self.parse_warning_data(response)
            print(f"warning data parsed: {warning_data}")
    
            return warning_data
    
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    
    
    def get_capacity_data(bms_connection, pack_number=None):
        try:
            # Generate request
            request = generate_bms_request("capacity", pack_number)
            
            # Send request to BMS
            if not send_data_to_bms(bms_connection, request):
                return None
            
            # Receive response from BMS
            response = receive_data_from_bms(bms_connection)
            if response is None:
                return None
            
            # Parse capacity data from response
            capacity_data = parse_capacity_data(response)
            return capacity_data
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    
    
    def get_time_date_data(bms_connection, pack_number=None):
        
        try:
            # Generate request
            request = generate_bms_request("time_date",pack_number)
            
            # Send request to BMS
            if not send_data_to_bms(bms_connection, request):
                return None
            
            # Receive response from BMS
            response = receive_data_from_bms(bms_connection)
            if response is None:
                return None
            
            # Parse analog data from response
            time_date_data = parse_time_date_data(response)
            return time_date_data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    
    
    def get_product_info_data(bms_connection, pack_number=None):
        
        try:
            # Generate request
            request = generate_bms_request("product_info",pack_number)
            
            # Send request to BMS
            if not send_data_to_bms(bms_connection, request):
                return None
            
            # Receive response from BMS
            response = receive_data_from_bms(bms_connection)
            if response is None:
                return None
            
            # Parse analog data from response
            product_info_data = parse_product_info_data(response)
            return product_info_data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
