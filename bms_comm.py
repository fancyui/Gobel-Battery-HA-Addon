import serial
import socket
import logging

class BMSCommunication:
    def __init__(self, interface='serial', serial_port=None, baud_rate=None, ethernet_ip=None, ethernet_port=None,buffer_size=1024,debug=0):
        self.interface = interface
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.ethernet_ip = ethernet_ip
        self.ethernet_port = ethernet_port
        self.buffer_size = buffer_size
        self.bms_connection = None

        # Configure logging
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def connect(self):
        if self.interface == 'serial' and self.serial_port and self.baud_rate:
            try:
                self.logger.info(f"Trying to connect BMS over {self.serial_port}:{self.baud_rate}")
                self.bms_connection = serial.Serial(self.serial_port, self.baud_rate, timeout=3)
                self.logger.info(f"Connected to BMS over serial port: {self.serial_port} with baud rate: {self.baud_rate}")
                self.logger.info("Please ensure the Baud Rate is correctly set. An incorrect baud rate may not raise an immediate error, but it can lead to communication failures or corrupted data.")

                return self.bms_connection
            except serial.SerialException as e:
                self.logger.error(f"Serial connection error: {e}")
                return None
        elif self.interface in ['ethernet', 'wifi'] and self.ethernet_ip and self.ethernet_port:
            try:
                self.logger.info(f"Trying to connect BMS over {self.ethernet_ip}:{self.ethernet_port}")
                self.bms_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.bms_connection.settimeout(3)
                self.bms_connection.connect((self.ethernet_ip, self.ethernet_port))
                self.logger.info(f"Connected to BMS over Ethernet: {self.ethernet_ip}:{self.ethernet_port}")
                return self.bms_connection
            except socket.error as e:
                self.logger.error(f"Ethernet connection error: {e}")
                return None
        else:
            self.logger.error("Invalid parameters or interface selection.")
            return None


    def disconnect(self):
        if self.bms_connection:
            if self.interface == 'serial':
                try:
                    self.bms_connection.close()
                    self.logger.debug(f"Disconnected from BMS over serial port: {self.serial_port}")
                except serial.SerialException as e:
                    self.logger.error(f"Error while disconnecting serial connection: {e}")
            
            elif self.interface in ['ethernet', 'wifi']:
                try:
                    self.bms_connection.close()
                    self.logger.debug(f"Disconnected from BMS over Ethernet: {self.ethernet_ip}:{self.ethernet_port}")
                except socket.error as e:
                    self.logger.error(f"Error while disconnecting Ethernet connection: {e}")
            
            # Set connection to None after closing it.
            self.bms_connection = None
        else:
            self.logger.warning("No active connection to disconnect.")




    def send_data(self, data):
        try:
            # Ensure data is in bytes format
            if isinstance(data, str):
                data = data.encode()  # Convert string to bytes if necessary

            # Check if the connection is a socket (Ethernet)
            if hasattr(self.bms_connection, 'send'):
                sent_bytes = self.bms_connection.send(data)
                self.logger.debug(f"Sent data via TCP: {data.hex().upper()}")
                
            # Check if the connection is a serial connection
            elif hasattr(self.bms_connection, 'write'):
                sent_bytes = self.bms_connection.write(data)
                self.logger.debug(f"Sent data via serial: {data.hex().upper()}")
            else:
                raise ValueError("Unsupported connection type")
            return True

        except Exception as e:
            self.logger.error(f"Error sending data to BMS: {e}")
            self.connect()
            return False

    def receive_data(self, return_raw=False):
        try:
            # Check if the connection is a serial connection
            if hasattr(self.bms_connection, 'readline'):
                raw_data = self.bms_connection.readline()
                if return_raw:
                    return raw_data
                else:
                    received_data = raw_data.decode().strip()
            # Check if the connection is a socket (Ethernet)
            elif hasattr(self.bms_connection, 'recv'):
                if return_raw:
                    # For raw data, use dedicated TCP Modbus receiving logic
                    raw_data = self._receive_tcp_modbus_response()
                    if raw_data:
                        self.logger.debug(f"Received raw data (hex): {raw_data.hex().upper()}")
                        return raw_data
                    else:
                        return None
                else:
                    # Original string receiving method, for other BMS
                    raw_data = self.bms_connection.recv(self.buffer_size)
                    received_data = raw_data.decode().strip()
            else:
                raise ValueError("Unsupported connection type")

            if not return_raw:
                self.logger.debug(f"Received data from BMS: {received_data}")
                return received_data
        except Exception as e:
            # Log the raw data when there is a decoding error
            if 'raw_data' in locals():
                self.logger.error(f"Error receiving data from BMS: {e}. Raw data: {raw_data}")
                self.logger.error(f"Raw data (hex): {raw_data.hex()}")
            else:
                self.logger.warning(f"No data received from BMS: {e}")
            return None

    def _receive_tcp_modbus_response(self):
        """
        A dedicated method for receiving TCP Modbus RTU responses.
        """
        try:
            import time
            
            # Wait for BMS processing time after sending
            time.sleep(0.1)
            
            # Receive data
            all_data = b''
            max_attempts = 5
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    # Set timeout
                    original_timeout = self.bms_connection.gettimeout()
                    self.bms_connection.settimeout(1.0)
                    
                    chunk = self.bms_connection.recv(1024)
                    
                    # Restore original timeout setting
                    self.bms_connection.settimeout(original_timeout)
                    
                    if chunk:
                        all_data += chunk
                        self.logger.debug(f"Received {len(chunk)} bytes, total {len(all_data)} bytes")
                        
                        # Check if a complete Modbus response has been received
                        if len(all_data) >= 3:
                            device_addr, function_code, byte_count = all_data[0], all_data[1], all_data[2]
                            expected_length = 3 + byte_count + 2  # Header + Data + CRC
                            
                            if len(all_data) >= expected_length:
                                complete_response = all_data[:expected_length]
                                self.logger.debug(f"Successfully received complete Modbus response: {expected_length} bytes")
                                return complete_response
                        
                        # Wait a short while for more data
                        time.sleep(0.05)
                    else:
                        time.sleep(0.1)
                        
                except socket.timeout:
                    # Timeout is normal, continue trying
                    pass
                except Exception as e:
                    self.logger.warning(f"Error while receiving data: {e}")
                    
                attempt += 1
            
            if all_data:
                self.logger.debug(f"Received data, but it might be incomplete: {len(all_data)} bytes")
                return all_data
            else:
                self.logger.warning("No data received")
                return None
                
        except Exception as e:
            self.logger.error(f"Error receiving TCP Modbus response: {e}")
            return None

