#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import logging

class JKBMS485:
    """
    JK BMS RS485 Modbus Communication Class
    Implements RS485 Modbus communication with JK BMS, providing the same interface and data format as PACE BMS.
    """

    def __init__(self, bms_comm, ha_comm, bms_type, data_refresh_interval, debug, if_random):
        self.bms_comm = bms_comm
        self.ha_comm = ha_comm
        self.bms_type = bms_type
        self.data_refresh_interval = data_refresh_interval
        self.debug = debug
        self.if_random = if_random

        # Cumulative energy variables (for energy statistics)
        self.total_energy_charged = 0.0    # Cumulative charged energy (Wh)
        self.total_energy_discharged = 0.0  # Cumulative discharged energy (Wh)
        self.last_energy_time = None       # Timestamp of the last energy calculation
        
        # Configure logging
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Default slave address (JK BMS may use address 0)
        self.default_slave_address = 0x00
        self.address_detected = False  # Flag to indicate if address detection has been performed
        
        # Function code definitions
        self.FUNCTION_CODE_READ_HOLDING_REGISTERS = 0x03
        self.FUNCTION_CODE_WRITE_MULTIPLE_REGISTERS = 0x10
        
        # Register address definitions (based on JK BMS protocol document)
        # Configuration area base address: 0x1000, Data area base address: 0x1200, Version info area: 0x1400
        self.CONFIG_BASE_ADDRESS = 0x1000
        self.DATA_BASE_ADDRESS = 0x1200
        self.VERSION_BASE_ADDRESS = 0x1400
        
        # Data area register address mapping
        self.REGISTER_ADDRESSES = {
            # Cell Voltages (Base Address 0x1200)
            'CellVol0': 0x1200,      # Cell Voltage 0
            'CellVol1': 0x1202,      # Cell Voltage 1
            'CellVol2': 0x1204,      # Cell Voltage 2
            'CellVol3': 0x1206,      # Cell Voltage 3
            'CellVol4': 0x1208,      # Cell Voltage 4
            'CellVol5': 0x120A,      # Cell Voltage 5
            'CellVol6': 0x120C,      # Cell Voltage 6
            'CellVol7': 0x120E,      # Cell Voltage 7
            'CellVol8': 0x1210,      # Cell Voltage 8
            'CellVol9': 0x1212,      # Cell Voltage 9
            'CellVol10': 0x1214,     # Cell Voltage 10
            'CellVol11': 0x1216,     # Cell Voltage 11
            'CellVol12': 0x1218,     # Cell Voltage 12
            'CellVol13': 0x121A,     # Cell Voltage 13
            'CellVol14': 0x121C,     # Cell Voltage 14
            'CellVol15': 0x121E,     # Cell Voltage 15
            'CellVol16': 0x1220,     # Cell Voltage 16
            'CellVol17': 0x1222,     # Cell Voltage 17
            'CellVol18': 0x1224,     # Cell Voltage 18
            'CellVol19': 0x1226,     # Cell Voltage 19
            'CellVol20': 0x1228,     # Cell Voltage 20
            'CellVol21': 0x122A,     # Cell Voltage 21
            'CellVol22': 0x122C,     # Cell Voltage 22
            'CellVol23': 0x122E,     # Cell Voltage 23
            'CellVol24': 0x1230,     # Cell Voltage 24
            'CellVol25': 0x1232,     # Cell Voltage 25
            'CellVol26': 0x1234,     # Cell Voltage 26
            'CellVol27': 0x1236,     # Cell Voltage 27
            'CellVol28': 0x1238,     # Cell Voltage 28
            'CellVol29': 0x123A,     # Cell Voltage 29
            'CellVol30': 0x123C,     # Cell Voltage 30
            'CellVol31': 0x123E,     # Cell Voltage 31
            
            # Main Parameters
            'CellSta': 0x1240,       # Battery Status (UINT32)
            'CellVolAve': 0x1244,    # Average Cell Voltage (UINT16)
            'CellVdifMax': 0x1246,   # Max Voltage Difference (UINT16)
            'MaxMinVolCellNbr': 0x1248, # Max/Min Voltage Cell Number (UINT8*2)
            'TempMos': 0x128A,       # Power Board Temperature (INT16)
            'BatVol': 0x1290,        # Battery Total Voltage (UINT32)
            'BatWatt': 0x1294,       # Battery Power (UINT32)
            'BatCurrent': 0x1298,    # Battery Current (INT32)
            'TempBat1': 0x129C,      # Battery Temperature 1 (INT16)
            'TempBat2': 0x129E,      # Battery Temperature 2 (INT16)
            'AlarmSta': 0x12A0,      # Alarm Status (UINT32)
            'BalanCurrent': 0x12A4,  # Balancing Current (INT16)
            'BalanSOC': 0x12A6,      # Balancing Status and SOC (UINT8*2)
            'SOCCapRemain': 0x12A8,  # Remaining Capacity (INT32)
            'SOCFullChargeCap': 0x12AC, # Battery Actual Capacity (UINT32)
            'SOCCycleCount': 0x12B0, # Cycle Count (UINT32)
            'SOCCycleCap': 0x12B4,   # Total Cycle Capacity (UINT32)
            'SOCSOH': 0x12B8,        # SOH Estimation (UINT8)
            'UserAlarm': 0x12BA,     # User Level Alarm (UINT16)
            'RunTime': 0x12BC,       # Running Time (UINT32)
            'ChargeDischarge': 0x12C0, # Charge/Discharge Status (UINT8*2)
            'TempBat3': 0x12F8,      # Battery Temperature 3 (INT16)
            'TempBat4': 0x12FA,      # Battery Temperature 4 (INT16)
            'TempBat5': 0x12FC,      # Battery Temperature 5 (INT16)
            
            # Version Info Area Register Address Mapping (Base Address 0x1400)
            'HardwareVersion': 0x1410,  # Hardware Version (ASCII 8 bytes)
            'SoftwareVersion': 0x1418,  # Software Version (ASCII 8 bytes)
        }

    def calculate_crc16_modbus(self, data):
        """
        Calculate Modbus CRC16 checksum.
        
        Args:
            data (bytes): Data to calculate CRC for.
            
        Returns:
            int: CRC16 checksum.
        """
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

    def calculate_cumulative_energy(self, current_power_kw):
        """
        Calculate cumulative energy using actual time intervals.
        
        Args:
            current_power_kw (float): Current power (kW).
            
        Returns:
            tuple: (Cumulative charged energy Wh, Cumulative discharged energy Wh).
        """
        import time
        
        current_time = time.time()
        
        # Initialize timestamp on the first call
        if self.last_energy_time is None:
            self.last_energy_time = current_time
            return self.total_energy_charged, self.total_energy_discharged
        
        # Calculate actual time interval (seconds)
        time_interval = current_time - self.last_energy_time
        self.last_energy_time = current_time
        
        # Prevent abnormal time intervals
        if time_interval <= 0 or time_interval > 300:  # More than 5 minutes is considered abnormal
            self.logger.warning(f"Abnormal time interval: {time_interval}s, skipping energy calculation for this cycle")
            return self.total_energy_charged, self.total_energy_discharged
        
        # Calculate energy increment (Wh)
        # Power(kW) * Time(s) * 1000 / 3600 = Energy(Wh)
        if current_power_kw is not None:
            energy_delta = abs(current_power_kw) * time_interval * 1000 / 3600
            
            # Accumulate to the corresponding energy counter
            if current_power_kw >= 0:
                self.total_energy_charged += energy_delta
                self.logger.debug(f"Charge energy delta: {energy_delta:.3f}Wh, cumulative: {self.total_energy_charged:.3f}Wh")
            else:
                self.total_energy_discharged += energy_delta
                self.logger.debug(f"Discharge energy delta: {energy_delta:.3f}Wh, cumulative: {self.total_energy_discharged:.3f}Wh")
        
        return self.total_energy_charged, self.total_energy_discharged

    def reset_cumulative_energy(self):
        """
        Reset the cumulative energy counters.
        Used for manual reset or to restart statistics.
        """
        self.total_energy_charged = 0.0
        self.total_energy_discharged = 0.0
        self.last_energy_time = None
        self.logger.info("Cumulative energy counters have been reset")

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

    def build_read_register_command(self, register_address, register_count=1, slave_address=None):
        """
        Build a Modbus command to read registers.
        
        Args:
            register_address (int): Starting register address.
            register_count (int): Number of registers to read, defaults to 1.
            slave_address (int): Slave address, defaults to the one used in class initialization.
            
        Returns:
            bytes: The constructed Modbus command.
        """
        if slave_address is None:
            slave_address = self.default_slave_address
            
        # Build the command frame (without CRC)
        command_frame = struct.pack('>BBHH', 
                                  slave_address,                              # Address code (1 byte)
                                  self.FUNCTION_CODE_READ_HOLDING_REGISTERS,  # Function code (1 byte)
                                  register_address,                           # Starting register address (2 bytes, big-endian)
                                  register_count)                             # Number of registers (2 bytes, big-endian)
        
        # Calculate CRC checksum
        crc = self.calculate_crc16_modbus(command_frame)
        
        # Add CRC checksum (little-endian)
        command_with_crc = command_frame + struct.pack('<H', crc)
        
        self.logger.debug(f"Built command: {command_with_crc.hex().upper()}")
        
        return command_with_crc

    def parse_register_response(self, response):
        """
        Parse the response for reading registers.
        
        Args:
            response (bytes): Response data from the BMS.
            
        Returns:
            list: A list of parsed register values.
        """
        if len(response) < 5:
            self.logger.error("Response data length is insufficient")
            return None
            
        # Verify CRC checksum
        data_without_crc = response[:-2]
        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = self.calculate_crc16_modbus(data_without_crc)
        
        if received_crc != calculated_crc:
            self.logger.error(f"CRC check failed: received={received_crc:04X}, calculated={calculated_crc:04X}")
            return None
            
        # Parse the response data
        slave_address = response[0]
        function_code = response[1]
        byte_count = response[2]
        
        if function_code != self.FUNCTION_CODE_READ_HOLDING_REGISTERS:
            self.logger.error(f"Function code mismatch: {function_code:02X}")
            return None
            
        # Extract register data
        register_data = response[3:3+byte_count]
        register_values = []
        
        # Each register is 2 bytes, big-endian
        for i in range(0, len(register_data), 2):
            if i+1 < len(register_data):
                value = struct.unpack('>H', register_data[i:i+2])[0]
                register_values.append(value)
                
        return register_values

    def set_slave_address(self, address):
        """
        Set the slave address.
        
        Args:
            address (int): Slave address (0-247).
        """
        if 0 <= address <= 247:
            self.default_slave_address = address
            self.logger.info(f"Slave address set to: {address}")
        else:
            raise ValueError("Slave address must be in the range 0-247")

    def auto_detect_slave_address(self):
        """
        Automatically detect the slave address (tries addresses 0 and 1).
        
        Returns:
            int: Detected slave address, or None on failure.
        """
        try:
            # Try common slave addresses
            test_addresses = [0x00, 0x01]
            
            for addr in test_addresses:
                self.logger.debug(f"Trying slave address: {addr}")
                self.default_slave_address = addr
                
                # Try reading a simple register to test the connection
                register_values = self.read_register_data('BatVol', 2)
                
                if register_values is not None:
                    self.logger.info(f"Auto-detected slave address: {addr}")
                    return addr
                    
            self.logger.warning("Could not auto-detect a valid slave address")
            # Restore default address
            self.default_slave_address = 0x00
            return None
            
        except Exception as e:
            self.logger.error(f"Error during slave address auto-detection: {e}")
            return None

    def read_register_data(self, register_name, register_count=1):
        """
        Read data from a specified register.
        
        Args:
            register_name (str): The name of the register.
            register_count (int): The number of registers to read.
            
        Returns:
            list: A list of register values, or None on failure.
        """
        try:
            if register_name not in self.REGISTER_ADDRESSES:
                self.logger.error(f"Unknown register name: {register_name}")
                return None
                
            register_address = self.REGISTER_ADDRESSES[register_name]
            
            # Build the read command
            command = self.build_read_register_command(register_address, register_count)
            self.logger.debug(f"Read register {register_name} command: {command.hex().upper()}")
            
            # Send the command to the BMS
            if not self.bms_comm.send_data(command):
                self.logger.error("Failed to send command")
                return None
                
            # Receive the response - using raw binary data format
            response = self.bms_comm.receive_data(return_raw=True)
            if response is None:
                self.logger.error("Failed to receive response")
                return None
                
            self.logger.debug(f"Received response: {response.hex().upper()}")
            
            # Parse the response
            register_values = self.parse_register_response(response)
            return register_values
            
        except Exception as e:
            self.logger.error(f"Error reading register {register_name}: {e}")
            return None

    def get_cell_voltages(self, cell_count=16):
        """
        Get all cell voltages.
        
        Args:
            cell_count (int): Number of cells, defaults to 16.
            
        Returns:
            list: A list of cell voltages (mV), or None on failure.
        """
        try:
            # Read all cell voltages, starting from CellVol0
            register_values = self.read_register_data('CellVol0', cell_count)
            
            if register_values is None:
                return None
                
            # Convert to mV
            cell_voltages = []
            for i, voltage in enumerate(register_values):
                if voltage > 0:  # Filter out invalid voltages
                    cell_voltages.append(voltage)
                    
            self.logger.debug(f"Read {len(cell_voltages)} cell voltages: {cell_voltages}")
            return cell_voltages
            
        except Exception as e:
            self.logger.error(f"Error getting cell voltages: {e}")
            return None

    def get_battery_voltage(self):
        """
        Get the total battery voltage.
        
        Returns:
            float: Total battery voltage (V), or None on failure.
        """
        try:
            # Read battery total voltage register (UINT32, 2 registers)
            register_values = self.read_register_data('BatVol', 2)
            
            if register_values and len(register_values) >= 2:
                # Combine 32-bit value: high 16 bits + low 16 bits
                voltage_mv = (register_values[0] << 16) | register_values[1]
                voltage_v = voltage_mv / 1000.0  # Convert to V
                
                self.logger.debug(f"Battery total voltage: {voltage_v}V ({voltage_mv}mV)")
                return voltage_v
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting battery voltage: {e}")
            return None

    def get_battery_current(self):
        """
        Get the battery current.
        
        Returns:
            float: Battery current (A), or None on failure.
        """
        try:
            # Read battery current register (INT32, 2 registers)
            register_values = self.read_register_data('BatCurrent', 2)
            
            if register_values and len(register_values) >= 2:
                # Combine 32-bit signed value
                current_ma = (register_values[0] << 16) | register_values[1]
                
                # Handle signed number
                if current_ma & 0x80000000:
                    current_ma = current_ma - 0x100000000
                    
                current_a = current_ma / 1000.0  # Convert to A
                
                self.logger.debug(f"Battery current: {current_a}A ({current_ma}mA)")
                return current_a
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting battery current: {e}")
            return None

    def get_battery_power(self):
        """
        Get the battery power.
        
        Returns:
            float: Battery power (kW), or None on failure.
        """
        try:
            # Read battery power register (UINT32, 2 registers)
            register_values = self.read_register_data('BatWatt', 2)
            
            if register_values and len(register_values) >= 2:
                # Combine 32-bit value
                power_mw = (register_values[0] << 16) | register_values[1]
                power_kw = power_mw / 1000000.0  # Convert to kW
                
                self.logger.debug(f"Battery power: {power_kw}kW ({power_mw}mW)")
                return power_kw
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting battery power: {e}")
            return None

    def get_balance_current(self):
        """
        Get the balancing current.
        
        Returns:
            float: Balancing current (A), or None on failure.
        """
        try:
            # Read balancing current register (INT16, 1 register)
            register_values = self.read_register_data('BalanCurrent', 1)
            
            if register_values and len(register_values) > 0:
                # INT16, signed 16-bit value, unit is mA
                balance_current_ma = register_values[0]
                
                # Handle signed number
                if balance_current_ma & 0x8000:
                    balance_current_ma = balance_current_ma - 0x10000
                    
                balance_current_a = balance_current_ma / 1000.0  # Convert to A
                
                self.logger.debug(f"Balance current: {balance_current_a}A ({balance_current_ma}mA)")
                return balance_current_a
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting balance current: {e}")
            return None

    def get_version_info(self):
        """
        Get version information.
        
        Returns:
            dict: A dictionary containing hardware and software versions, or None on failure.
        """
        try:
            version_info = {}
            
            # Get hardware version (ASCII 8 bytes = 4 registers)
            hw_version_values = self.read_register_data('HardwareVersion', 4)
            if hw_version_values and len(hw_version_values) >= 4:
                self.logger.debug(f"Hardware version register values: {hw_version_values}")
                
                # Convert register values to ASCII string
                hw_version_bytes = b''
                for value in hw_version_values:
                    # Each register contains 2 bytes, big-endian
                    hw_version_bytes += struct.pack('>H', value)
                
                self.logger.debug(f"Hardware version byte data: {hw_version_bytes.hex()}")
                
                # Convert to string and remove null characters
                hw_version = hw_version_bytes.decode('ascii', errors='ignore').rstrip('\x00')
                self.logger.debug(f"Hardware version raw string: '{hw_version}' (length: {len(hw_version)})")
                
                # Further clean the string, remove all control characters and whitespace
                hw_version = ''.join(char for char in hw_version if char.isprintable()).strip()
                self.logger.debug(f"Hardware version cleaned: '{hw_version}' (length: {len(hw_version)})")
                
                # If the version is empty, set a default value
                if not hw_version:
                    hw_version = "Unknown"
                    self.logger.warning("Hardware version is empty, setting to Unknown")
                
                version_info['hardware_version'] = hw_version
                self.logger.debug(f"Hardware version: {hw_version}")
            
            # Get software version (ASCII 8 bytes = 4 registers)
            sw_version_values = self.read_register_data('SoftwareVersion', 4)
            if sw_version_values and len(sw_version_values) >= 4:
                self.logger.debug(f"Software version register values: {sw_version_values}")
                
                # Convert register values to ASCII string
                sw_version_bytes = b''
                for value in sw_version_values:
                    # Each register contains 2 bytes, big-endian
                    sw_version_bytes += struct.pack('>H', value)
                
                self.logger.debug(f"Software version byte data: {sw_version_bytes.hex()}")
                
                # Convert to string and remove null characters
                sw_version = sw_version_bytes.decode('ascii', errors='ignore').rstrip('\x00')
                self.logger.debug(f"Software version raw string: '{sw_version}' (length: {len(sw_version)})")
                
                # Further clean the string, remove all control characters and whitespace
                sw_version = ''.join(char for char in sw_version if char.isprintable()).strip()
                self.logger.debug(f"Software version cleaned: '{sw_version}' (length: {len(sw_version)})")
                
                # If the version is empty, set a default value
                if not sw_version:
                    sw_version = "Unknown"
                    self.logger.warning("Software version is empty, setting to Unknown")
                
                version_info['software_version'] = sw_version
                self.logger.debug(f"Software version: {sw_version}")
            
            self.logger.debug(f"Final version info: {version_info}")
            return version_info if version_info else None
            
        except Exception as e:
            self.logger.error(f"Error getting version info: {e}")
            return None

    def get_temperatures(self):
        """
        Get temperature information.
        
        Returns:
            list: A list of temperatures (°C), or None on failure.
        """
        try:
            temperatures = []
            
            # Read individual temperature sensors
            temp_registers = ['TempBat1', 'TempBat2', 'TempBat3', 'TempBat4', 'TempBat5', 'TempMos']
            
            for temp_reg in temp_registers:
                register_values = self.read_register_data(temp_reg, 1)
                
                if register_values and len(register_values) > 0:
                    # INT16, signed 16-bit value, unit is 0.1°C
                    temp_raw = register_values[0]
                    
                    # Handle signed number
                    if temp_raw & 0x8000:
                        temp_raw = temp_raw - 0x10000
                        
                    temp_celsius = temp_raw / 10.0  # Convert to °C
                    
                    # Only add reasonable temperature values
                    if -50 <= temp_celsius <= 150:
                        temperatures.append(temp_celsius)
                        
            self.logger.debug(f"Read {len(temperatures)} temperatures: {temperatures}")
            return temperatures
            
        except Exception as e:
            self.logger.error(f"Error getting temperatures: {e}")
            return None

    def get_soc_data(self):
        """
        Get SOC related data.
        
        Returns:
            dict: A dictionary of SOC data, or None on failure.
        """
        try:
            soc_data = {}
            
            # Read balancing status and SOC register
            balan_soc_values = self.read_register_data('BalanSOC', 1)
            if balan_soc_values and len(balan_soc_values) > 0:
                # Split into two UINT8 values
                value = balan_soc_values[0]
                balan_state = (value >> 8) & 0xFF  # High byte: balancing status
                soc = value & 0xFF                 # Low byte: SOC
                
                soc_data['view_SOC'] = float(soc)
                soc_data['balance_state'] = balan_state
                
            # Read remaining capacity (INT32)
            remain_cap_values = self.read_register_data('SOCCapRemain', 2)
            if remain_cap_values and len(remain_cap_values) >= 2:
                remain_cap_mah = (remain_cap_values[0] << 16) | remain_cap_values[1]
                # Handle signed number
                if remain_cap_mah & 0x80000000:
                    remain_cap_mah = remain_cap_mah - 0x100000000
                soc_data['view_remain_capacity'] = remain_cap_mah / 1000.0  # Convert to Ah
                
            # Read full charge capacity (UINT32)
            full_cap_values = self.read_register_data('SOCFullChargeCap', 2)
            if full_cap_values and len(full_cap_values) >= 2:
                full_cap_mah = (full_cap_values[0] << 16) | full_cap_values[1]
                soc_data['view_full_capacity'] = full_cap_mah / 1000.0  # Convert to Ah
                
            # Read cycle count (UINT32)
            cycle_values = self.read_register_data('SOCCycleCount', 2)
            if cycle_values and len(cycle_values) >= 2:
                cycle_count = (cycle_values[0] << 16) | cycle_values[1]
                soc_data['view_cycle_number'] = cycle_count
                
            # Read SOH
            soh_values = self.read_register_data('SOCSOH', 1)
            if soh_values and len(soh_values) > 0:
                # SOH is in the high byte of the UINT8
                value = soh_values[0]
                soh = (value >> 8) & 0xFF
                soc_data['view_SOH'] = float(soh)
                
            self.logger.debug(f"SOC data: {soc_data}")
            return soc_data
            
        except Exception as e:
            self.logger.error(f"Error getting SOC data: {e}")
            return None

    def parse_analog_data(self, raw_data):
        """
        Parse analog data, maintaining the same data structure as PACE BMS.
        
        Args:
            raw_data (dict): Raw data read from registers.
            
        Returns:
            list: A list of parsed pack data.
        """
        try:
            packs_data = []
            pack_data = {}
            
            # Cell voltage data
            cell_voltages = raw_data.get('cell_voltages', [])
            pack_data['cell_voltages'] = cell_voltages
            pack_data['view_num_cells'] = len(cell_voltages)
            
            if cell_voltages:
                cell_voltage_max = max(cell_voltages)
                cell_voltage_min = min(cell_voltages)
                cell_voltage_max_index = cell_voltages.index(cell_voltage_max) + 1
                cell_voltage_min_index = cell_voltages.index(cell_voltage_min) + 1

                pack_data['cell_voltage_max'] = cell_voltage_max
                pack_data['cell_voltage_min'] = cell_voltage_min
                pack_data['cell_voltage_max_index'] = cell_voltage_max_index
                pack_data['cell_voltage_min_index'] = cell_voltage_min_index
                pack_data['cell_voltage_diff'] = cell_voltage_max - cell_voltage_min
            else:
                pack_data['cell_voltage_max'] = 0
                pack_data['cell_voltage_min'] = 0
                pack_data['cell_voltage_max_index'] = 0
                pack_data['cell_voltage_min_index'] = 0
                pack_data['cell_voltage_diff'] = 0

            # Temperature data
            temperatures = raw_data.get('temperatures', [])
            pack_data['temperatures'] = temperatures
            pack_data['view_num_temps'] = len(temperatures)

            # Current data
            current = raw_data.get('current', 0.0)
            pack_data['view_current'] = current

            # Voltage data
            voltage = raw_data.get('voltage', 0.0)
            pack_data['view_voltage'] = voltage

            # Power data
            power = raw_data.get('power', 0.0)
            pack_data['view_power'] = power

            # Calculate cumulative energy data (using actual time intervals)
            charged_total, discharged_total = self.calculate_cumulative_energy(power)
            pack_data['view_energy_charged'] = round(charged_total, 2)
            pack_data['view_energy_discharged'] = round(discharged_total, 2)

            # SOC related data
            soc_data = raw_data.get('soc_data', {})
            pack_data['view_remain_capacity'] = soc_data.get('view_remain_capacity', 0.0)
            pack_data['view_full_capacity'] = soc_data.get('view_full_capacity', 0.0)
            pack_data['view_cycle_number'] = soc_data.get('view_cycle_number', 0)
            pack_data['view_SOC'] = soc_data.get('view_SOC', 0.0)
            pack_data['view_SOH'] = soc_data.get('view_SOH', 0.0)

            # Estimate design capacity (based on full charge capacity)
            pack_data['view_design_capacity'] = pack_data['view_full_capacity']

            # Balancing current data
            balance_current = raw_data.get('balance_current', 0.0)
            pack_data['view_balance_current'] = balance_current

            # Version info data
            version_info = raw_data.get('version_info', {})
            pack_data['hardware_version'] = version_info.get('hardware_version', '')
            pack_data['software_version'] = version_info.get('software_version', '')

            packs_data.append(pack_data)
            
            self.logger.debug(f"Finished parsing analog data: {pack_data}")
            return packs_data

        except Exception as e:
            self.logger.error(f"Error parsing analog data: {e}")
            return None

    def get_analog_data(self, pack_number=None):
        """
        Get analog data, maintaining the same interface as PACE BMS.
        
        Args:
            pack_number: Pack number (JK BMS usually has only one pack).
            
        Returns:
            list: A list containing analog data.
        """
        try:
            self.logger.debug("Starting to get JK BMS analog data")
            
            # Auto-detect slave address on the first call
            if not self.address_detected:
                self.logger.info("First connection, starting auto-detection of slave address...")
                detected_address = self.auto_detect_slave_address()
                if detected_address is not None:
                    self.address_detected = True
                else:
                    self.logger.warning("Address detection failed, continuing with default address 0")
            
            # Collect all raw data
            raw_data = {}
            
            # Get cell voltages
            cell_voltages = self.get_cell_voltages(32)  # Supports up to 32 cells
            if cell_voltages:
                raw_data['cell_voltages'] = cell_voltages
            else:
                self.logger.warning("Failed to get cell voltages")
                raw_data['cell_voltages'] = []

            # Get temperatures
            temperatures = self.get_temperatures()
            if temperatures:
                raw_data['temperatures'] = temperatures
            else:
                self.logger.warning("Failed to get temperatures")
                raw_data['temperatures'] = []

            # Get current
            current = self.get_battery_current()
            raw_data['current'] = current if current is not None else 0.0

            # Get voltage
            voltage = self.get_battery_voltage()
            raw_data['voltage'] = voltage if voltage is not None else 0.0

            # Get power
            power = self.get_battery_power()
            raw_data['power'] = power if power is not None else 0.0

            # Get SOC data
            soc_data = self.get_soc_data()
            raw_data['soc_data'] = soc_data if soc_data else {}

            # Get balancing current
            balance_current = self.get_balance_current()
            raw_data['balance_current'] = balance_current if balance_current is not None else 0.0

            # Get version info
            version_info = self.get_version_info()
            raw_data['version_info'] = version_info if version_info else {}

            # Parse data into PACE BMS format
            analog_data = self.parse_analog_data(raw_data)
            
            self.logger.debug(f"Finished getting JK BMS analog data: {analog_data}")
            return analog_data

        except Exception as e:
            self.logger.error(f"Error getting analog data: {e}")
            return None

    def get_warning_data(self, pack_number=None):
        """
        Get warning data, maintaining the same interface as PACE BMS.
        
        Args:
            pack_number: Pack number.
            
        Returns:
            list: A list containing warning data.
        """
        try:
            self.logger.debug("Starting to get JK BMS warning data")
            
            # Read alarm status register
            alarm_values = self.read_register_data('AlarmSta', 2)
            
            warning_data = []
            pack_warning = {
                'cell_number': len(self.get_cell_voltages(32) or []),
                'cell_voltage_warnings': [],
                'temp_sensor_number': len(self.get_temperatures() or []),
                'temp_sensor_warnings': [],
                'warn_charge_current': 'normal',
                'warn_total_voltage': 'normal',
                'warn_discharge_current': 'normal',
                'protect_state_1': {},
                'protect_state_2': {},
                'instruction_state': {},
                'control_state': {},
                'fault_state': {},
                'balance_state_1': 0,
                'balance_state_2': 0,
                'warn_state_1': {},
                'warn_state_2': {}
            }
            
            if alarm_values and len(alarm_values) >= 2:
                # Combine 32-bit alarm status
                alarm_status = (alarm_values[0] << 16) | alarm_values[1]
                
                # Parse various alarm statuses
                pack_warning['protect_state_1'] = {
                    'protect_short_circuit': bool(alarm_status & (1 << 7)),
                    'protect_high_discharge_current': bool(alarm_status & (1 << 13)),
                    'protect_high_charge_current': bool(alarm_status & (1 << 6)),
                    'protect_low_total_voltage': bool(alarm_status & (1 << 12)),
                    'protect_high_total_voltage': bool(alarm_status & (1 << 5)),
                    'protect_low_cell_voltage': bool(alarm_status & (1 << 11)),
                    'protect_high_cell_voltage': bool(alarm_status & (1 << 4)),
                }
                
                pack_warning['protect_state_2'] = {
                    'status_fully_charged': False,  # This status does not exist in JK BMS
                    'protect_low_env_temp': bool(alarm_status & (1 << 9)),
                    'protect_high_env_temp': bool(alarm_status & (1 << 8)),
                    'protect_high_MOS_temp': bool(alarm_status & (1 << 1)),
                    'protect_low_discharge_temp': bool(alarm_status & (1 << 15)),
                    'protect_low_charge_temp': bool(alarm_status & (1 << 9)),
                    'protect_high_discharge_temp': bool(alarm_status & (1 << 15)),
                    'protect_high_charge_temp': bool(alarm_status & (1 << 8)),
                }
                
                pack_warning['fault_state'] = {
                    'fault_sampling': bool(alarm_status & (1 << 3)),
                    'fault_cell': bool(alarm_status & (1 << 2)),
                    'fault_NTC': False,  # Determined by temperature sensor status
                    'fault_discharge_MOS': bool(alarm_status & (1 << 17)),
                    'fault_charge_MOS': bool(alarm_status & (1 << 16)),
                }

            # Populate cell voltage warnings (normal state)
            for i in range(pack_warning['cell_number']):
                pack_warning['cell_voltage_warnings'].append('normal')
                
            # Populate temperature sensor warnings (normal state)
            for i in range(pack_warning['temp_sensor_number']):
                pack_warning['temp_sensor_warnings'].append('normal')

            warning_data.append(pack_warning)
            
            self.logger.debug(f"Finished getting JK BMS warning data: {warning_data}")
            return warning_data

        except Exception as e:
            self.logger.error(f"Error getting warning data: {e}")
            return None

    def publish_analog_data_mqtt(self, pack_number=None):
        """
        Publish analog data to MQTT, maintaining the same interface and format as PACE BMS.
        
        Args:
            pack_number: Pack number.
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
            'view_power': 'measurement',
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

        # Publish overall data
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

        total_soc = round(total_remain_capacity / total_full_capacity * 100, 1) if total_full_capacity > 0 else 0
        self.ha_comm.publish_sensor_state(total_soc, '%', "total_SOC")
        self.ha_comm.publish_sensor_discovery("total_SOC", "%", icons['total_SOC'], deviceclasses['total_SOC'], stateclasses['total_SOC'])

        # Publish random data (if enabled)
        if self.if_random:
            import random
            random_number = random.randint(1, 100)
            self.ha_comm.publish_sensor_state(random_number, 'R', "random_number")
            self.ha_comm.publish_sensor_discovery("random_number", "R", icons['random_number'], deviceclasses['random_number'], stateclasses['random_number'])

        # Publish detailed data for each pack
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
                    # Add debug info, especially for version info
                    if key in ['hardware_version', 'software_version']:
                        self.logger.debug(f"Preparing to publish {key}: value='{value}', unit='{unit}', icon='{icon}'")
                    
                    self.ha_comm.publish_sensor_state(value, unit, f"pack_{pack_i:02}_{key}")
                    self.ha_comm.publish_sensor_discovery(f"pack_{pack_i:02}_{key}", unit, icon,deviceclass,stateclass)

    def publish_warning_data_mqtt(self, pack_number=None):
        """
        Publish warning data to MQTT, maintaining the same interface and format as PACE BMS.
        
        Args:
            pack_number: Pack number.
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
            pack_i = pack_i + 1
            for key, value in pack.items():
                if key == 'cell_voltage_warnings':
                    cell_i = 0
                    icon = "mdi:battery-heart-variant"
                    for cell_voltage_warning in value:
                        cell_i = cell_i + 1
                        self.ha_comm.publish_warn_state(cell_voltage_warning, f"pack_{pack_i:02}_cell_voltage_warning_{cell_i:02}")
                        self.ha_comm.publish_warn_discovery(f"pack_{pack_i:02}_cell_voltage_warning_{cell_i:02}",icon)
                        
                elif key == 'protect_state_1':
                    icon = "mdi:battery-alert"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}",icon)
                        
                elif key == 'fault_state':
                    icon = "mdi:alert"
                    for sub_key, sub_value in value.items():
                        self.ha_comm.publish_binary_sensor_state(sub_value, f"pack_{pack_i:02}_{sub_key}")
                        self.ha_comm.publish_binary_sensor_discovery(f"pack_{pack_i:02}_{sub_key}",icon) 

# Example usage
if __name__ == "__main__":
    """
    Usage example:
    This example shows how to create a JKBMS485 instance and get data.
    Note: You need to configure the communication interface and Home Assistant communication first.
    """
    
    # Mock communication interface (replace with a real serial communication class in actual use)
    class MockBMSComm:
        def send_data(self, data):
            print(f"Sending data: {data.hex().upper()}")
            return True
            
        def receive_data(self, return_raw=False):
            # Simulate returned data (in actual use, return data received from BMS)
            return b'\x01\x03\x02\x10\x00\x85\xC9'  # Example response data
    
    class MockHAComm:
        def publish_sensor_state(self, value, unit, topic):
            print(f"Publishing sensor state: {topic} = {value} {unit}")
            
        def publish_sensor_discovery(self, name, unit, icon, device_class, state_class):
            print(f"Publishing sensor discovery: {name}")
    
    # Create JK BMS instance
    mock_bms_comm = MockBMSComm()
    mock_ha_comm = MockHAComm()
    
    jk_bms = JKBMS485(
        bms_comm=mock_bms_comm,
        ha_comm=mock_ha_comm,
        bms_type="JK_BMS_RS485",
        data_refresh_interval=10,
        debug=True,
        if_random=False
    )
    
    print("=== JK BMS RS485 Modbus Communication Class Test ===")
    print("Class Function Description:")
    print("1. Supports full Modbus protocol communication")
    print("2. Provides the same interface and data format as PACE BMS")
    print("3. Supports reading parameters such as cell voltage, temperature, current, power, etc.")
    print("4. Supports alarm status monitoring")
    print("5. Fully compatible with Home Assistant MQTT publishing")
    print()
    
    print("Supported main functions:")
    print("- get_analog_data(): Get all analog data")
    print("- get_warning_data(): Get warning data")
    print("- publish_analog_data_mqtt(): Publish analog data to MQTT")
    print("- publish_warning_data_mqtt(): Publish warning data to MQTT")
    print("- get_cell_voltages(): Get cell voltages")
    print("- get_battery_voltage(): Get total voltage")
    print("- get_battery_current(): Get current")
    print("- get_temperatures(): Get temperatures")
    print("- get_soc_data(): Get SOC related data")
    print()
    
    print("Data format is fully compatible with PACE BMS, including:")
    print("- Same field names and units")
    print("- Same MQTT topic structure")
    print("- Same Home Assistant device classes and state classes")
    print("- Same icons and display formats")
    print()
    
    # Set slave address
    jk_bms.set_slave_address(1)
    
    # Example of building read command
    command = jk_bms.build_read_register_command(0x1202, 1)  # Read cell voltage 1
    print(f"Example of read cell voltage 1 command: {command.hex().upper()}")
    print()
    
    print("=== Usage Instructions ===")
    print("1. Ensure RS485 interface is connected correctly")
    print("2. Configure the correct slave address (default 0x01)")
    print("3. Ensure the baud rate is 115200bps")
    print("4. Replace MockBMSComm with the actual serial communication class in actual use")
    print("5. Configure ha_comm with the actual Home Assistant MQTT communication class")
    print()
    
    print("Protocol Features:")
    print("- Based on standard Modbus RTU protocol")
    print("- Supports CRC16 check for data integrity")
    print("- Supports 1-247 slave addresses")
    print("- Data area base address: 0x1200")
    print("- Configuration area base address: 0x1000") 