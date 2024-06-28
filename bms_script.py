import serial
import socket
import struct
import paho.mqtt.client as mqtt
import time
import os
import json
import sys
import logging



# Define the load_config function
def load_config():
    config_path = '/data/options.json'
    if os.path.exists(config_path):
        logging.info("Loading options.json")
        try:
            with open(config_path) as file:
                config = json.load(file)
                logging.info("Config: " + json.dumps(config))
                return config
        except Exception as e:
            logging.error("Error loading configuration: %s", str(e))
            return None
    else:
        logging.warning("No config file found.")
        logging.warning("Please make a configuration in the panel")
        return None



# Load the configuration
config = load_config()

bms_connected = False
mqtt_connected = False
# Accessing the parameters
mqtt_broker = config.get('mqtt_broker')
mqtt_port = config.get('mqtt_port')
mqtt_username = config.get('mqtt_username')
mqtt_password = config.get('mqtt_password')
mqtt_enable_discovery = config.get('mqtt_enable_discovery')
mqtt_discovery_topic = config.get('mqtt_discovery_topic')
mqtt_base_topic = config.get('mqtt_base_topic')
interface = config.get('connection_type')
ethernet_ip = config.get('bms_ip_address')
ethernet_port = config.get('bms_ip_port')
serial_port = config.get('bms_usb_port')
baud_rate = config.get('bms_baud_rate')
data_refresh_interval = config.get('data_refresh_interval')
debug_output = config.get('debug_output')





def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global mqtt_connected
        mqtt_connected = True
        client.will_set(mqtt_topic + "/availability","online", qos=0, retain=False)
        print(f"Connected to MQTT Broker: {mqtt_broker}:{mqtt_port}")
    else:
        client.will_set(mqtt_topic + "/availability","offline", qos=0, retain=True)
        print(f"Failed to connect to MQTT Broker: {mqtt_broker}. Error code: {rc}")


def setup_mqtt_client():
    client = mqtt.Client()
    client.username_pw_set(username=mqtt_username, password=mqtt_password)
    client.on_connect = on_connect
    client.connect(mqtt_broker, mqtt_port, 60)
    return client



def send_data_to_mqtt(data):
    def on_connect(client, userdata, flags, rc):
        print(f"Connected to MQTT Broker with result code {rc}")

    def on_publish(client, userdata, mid):
        print(f"Data published to MQTT Broker with message id {mid}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()

    client.publish(mqtt_base_topic, data)
    print(f"Data sent to MQTT Broker: {data}")

    client.loop_stop()
    client.disconnect()



def connect_to_bms(interface='serial', serial_port=None, baud_rate=None, ethernet_ip=None, ethernet_port=None):
    if interface == 'serial' and serial_port:
        try:
            ser = serial.Serial(serial_port, baud_rate)
            print(f"Connected to BMS over serial port: {serial_port} with baud rate: {baud_rate}")
            return ser
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return None
    elif interface == 'ethernet' and ethernet_ip and ethernet_port:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ethernet_ip, ethernet_port))
            print(f"Connected to BMS over Ethernet: {ethernet_ip}:{ethernet_port}")
            return sock
        except socket.error as e:
            print(f"Ethernet connection error: {e}")
            return None
    else:
        print("Invalid parameters or interface selection.")
        return None

def send_data_to_bms(bms_connection, data):
    try:
        bms_connection.write(data.encode())  # Assuming data is a string, encode as needed
        print(f"Sent data to BMS: {data}")
        return True
    except Exception as e:
        print(f"Error sending data to BMS: {e}")
        return False

def receive_data_from_bms(bms_connection):
    try:
        received_data = bms_connection.readline().decode().strip()  # Assuming data is ASCII-encoded and newline terminated
        print(f"Received data from BMS: {received_data}")
        return received_data
    except Exception as e:
        print(f"Error receiving data from BMS: {e}")
        return None





def calculate_checksum(data):
    """
    Calculates the checksum for the given data.
    
    Parameters:
    data (bytes): The data for which to calculate the checksum.
    
    Returns:
    int: The calculated checksum.
    """
    chk_sum = sum(data) & 0xFF
    chk_sum = (0x100 - chk_sum) & 0xFF
    return chk_sum


def generate_bms_request(command_type, pack_number=None):
    """
    Generates a request to send to the BMS to get specific data based on the command parameter.
    
    Parameters:
    command_type (str): The type of command to send to the BMS.
                        It can be one of the following:
                        - 'analog' for getting all pack analog information.
                        - 'warning' for getting pack warning information.
                        - 'capacity' for getting pack capacity information.
                        - 'time_date' for getting pack time and date information.
                        - 'pack_number' for getting pack number.
                        - 'software_version' for getting software version information.
                        - 'product_info' for getting product information.
    pack_number (int, optional): The pack number to get information from. Defaults to None for all packs.
    
    Returns:
    bytes: The request message to be sent to the BMS.
    """

    
    SOI = 0x7E
    VER = 0x32
    ADR = 0x35
    EOI = 0x0D
    
    commands = {
        'analog': (0x30, 0x42, 0x02),
        'warning': (0x30, 0x44, 0x02),
        'capacity': (0x30, 0xA6, 0x02),
        'time_date': (0x30, 0xB1, 0x02),
        'pack_number': (0x46, 0x41, 0x00),
        'software_version': (0x46, 0xC1, 0x00),
        'product_info': (0x46, 0xC2, 0x00)
    }
    
    if command_type not in commands:
        raise ValueError("Invalid command type")
    
    CID1, CID2, length = commands[command_type]
    if pack_number is not None:
        COMMAND = f'{pack_number:02X}'
    else:
        COMMAND = 'FF'
    
    len_id = struct.pack('B', length)
    data = struct.pack('BBBBBB', SOI, VER, ADR, CID1, CID2, length) + struct.pack('BB', EOI)
    chk_sum = calculate_checksum(data)
    
    request = data[:-1] + struct.pack('B', chk_sum) + data[-1:]
    return request





def generate_mosfet_control_request(command_type, state):
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







def parse_analog_data(response):
    """
    Parses the ASCII response string to extract pack analog data for multiple packs.

    Args:
    response (str): The ASCII response string from the BMS.

    Returns:
    list: Parsed data containing pack analog information for each pack.
    """
    packs_data = []
    
    # Split the response into fields
    fields = response.split()
    
    # Check the command and response validity
    if fields[3] != '46' or fields[4] != '00':
        raise ValueError("Invalid command or response code")
    
    # Extract the length of the data information
    length = int(fields[5], 16)
    
    # Start parsing the data information
    offset = 6  # Start after fixed header fields

    # Number of packs
    num_packs = int(fields[offset], 16)
    offset += 1

    for _ in range(num_packs):
        pack_data = {}

        # Number of cells
        num_cells = int(fields[offset], 16)
        offset += 1
        pack_data['num_cells'] = int(num_cells)

        # Cell voltages
        cell_voltages = []
        for _ in range(num_cells):
            voltage = int(fields[offset], 16) # mV
            cell_voltages.append(voltage)
            offset += 1
        pack_data['cell_voltages'] = cell_voltages

        # Number of temperature sensors
        num_temps = int(fields[offset], 16)
        offset += 1
        pack_data['num_temps'] = num_temps

        # Temperatures
        temperatures = []
        for _ in range(num_temps):
            temperature = round(float(fields[offset])  / 10 - 273.15, 2)  # Convert tenths of degrees Kelvin to degrees Celsius

            temperatures.append(temperature)
            offset += 1
        pack_data['temperatures'] = temperatures

        # Pack current
        pack_current = round(float(fields[offset]) / 100, 2)  # Convert 10mA to A
        if pack_current > 32767:
            pack_current -= 65536
        offset += 1
        pack_data['pack_current'] = pack_current

        # Pack total voltage
        pack_total_voltage = round(float(fields[offset]) / 1000, 2)  # Convert mV to V
        offset += 1
        pack_data['pack_total_voltage'] = pack_total_voltage

        # Pack remaining capacity
        pack_remain_capacity = round(float(fields[offset]) / 100, 2)  # Convert 10mAH to AH
        offset += 1
        pack_data['pack_remain_capacity'] = pack_remain_capacity

        # Pack full capacity
        pack_full_capacity = round(float(fields[offset]) / 100, 2)  # Convert 10mAH to AH
        offset += 1
        pack_data['pack_full_capacity'] = pack_full_capacity

        # Pack design capacity
        pack_design_capacity = round(float(fields[offset]) / 100, 2)  # Convert 10mAH to AH
        offset += 1
        pack_data['pack_design_capacity'] = pack_design_capacity

        packs_data.append(pack_data)

    return packs_data





def parse_warning_data(data):
    """
    Parses the warning data received from the BMS.
    
    Parameters:
    data (str): The raw data string received from the BMS.
    
    Returns:
    dict: Parsed warning information.
    """
    fields = data.split()
    warnings = {
        'over_voltage': fields[0],
        'under_voltage': fields[1],
        'over_temperature': fields[2],
        'under_temperature': fields[3],
        'over_current': fields[4],
        'short_circuit': fields[5],
        'communication_error': fields[6]
    }
    return warnings

def parse_capacity_data(data):
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


def parse_time_date_data(data):
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


def parse_pack_number_data(data):
    """
    Parses the pack number data received from the BMS.
    
    Parameters:
    data (str): The raw data string received from the BMS.
    
    Returns:
    int: The pack number.
    """
    return int(data.strip(), 16)


def parse_software_version_data(data):
    """
    Parses the software version data received from the BMS.
    
    Parameters:
    data (str): The raw data string received from the BMS.
    
    Returns:
    str: The software version.
    """
    return data.strip()


def parse_product_info_data(data):
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




def get_analog_data(bms_connection, pack_number=None):
    
    try:
        # Generate request
        request = generate_bms_request("analog",pack_number)
        
        # Send request to BMS
        if not send_data_to_bms(bms_connection, request):
            return None
        
        # Receive response from BMS
        response = receive_data_from_bms(bms_connection)
        if response is None:
            return None
        
        # Parse analog data from response
        analog_data = parse_analog_data(response)
        return analog_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_warning_data(bms_connection, pack_number=None):
    
    try:
        # Generate request
        request = generate_bms_request("warning",pack_number)
        
        # Send request to BMS
        if not send_data_to_bms(bms_connection, request):
            return None
        
        # Receive response from BMS
        response = receive_data_from_bms(bms_connection)
        if response is None:
            return None
        
        # Parse analog data from response
        warning_data = parse_warning_data(response)
        return warning_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def get_capacity_data(bms_connection, pack_number=None):
    
    try:
        # Generate request
        request = generate_bms_request("capacity",pack_number)
        
        # Send request to BMS
        if not send_data_to_bms(bms_connection, request):
            return None
        
        # Receive response from BMS
        response = receive_data_from_bms(bms_connection)
        if response is None:
            return None
        
        # Parse analog data from response
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

        

def publish_data_to_mqtt(mqtt_base_topic, packs_data):
    for pack_index, pack_data in enumerate(packs_data):
        pack_topic = f"{mqtt_base_topic}/pack_{pack_index}"  # Secondary topic for each pack's data

        for key, value in pack_data.items():
            field_topic = f"{pack_topic}/{key}"  # Topic for each field in the pack data

            if isinstance(value, list):
                value_str = ','.join(str(val) for val in value)
            else:
                value_str = str(value)

            publish_to_mqtt(field_topic, value_str)


def run():
    # Connect to BMS
    bms_connection = connect_to_bms(interface, serial_port, baud_rate, ethernet_ip, ethernet_port)
    if bms_connection is None:
        return
    
    # Connect to MQTT
    mqtt_client = setup_mqtt_client()
    mqtt_client.loop_start()

    initial_data_fetched = False  # Flag to track if initial data has been fetched

    try:
        while True:  # Run continuously
            if not initial_data_fetched:
                # Get initial data
                get_capacity_data(bms_connection, pack_number=None)
                get_time_date_data(bms_connection, pack_number=None)
                get_product_info_data(bms_connection, pack_number=None)
                initial_data_fetched = True  # Set the flag to True after fetching initial data
            
            # Fetch analog and warning data every 5 seconds
            get_analog_data(bms_connection, pack_number=None)
            get_warning_data(bms_connection, pack_number=None)
            time.sleep(5)  # Sleep for 5 seconds between each iteration

    except KeyboardInterrupt:
        print("Stopping the program...")
    
    finally:
        mqtt_client.loop_stop()

if __name__ == "__main__":
    run()
