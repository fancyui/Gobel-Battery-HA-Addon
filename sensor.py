import serial
import socket
import struct
import paho.mqtt.client as mqtt
import time
import os
import json
import sys
import logging
import requests
import pacebms



# Define the load_config function
def load_config():
    config_path = '/data/options.json'
    if os.path.exists(config_path):
        print("Loading options.json")
        try:
            with open(config_path) as file:
                config = json.load(file)
                print("Config: " + json.dumps(config))
                return config
        except Exception as e:
            print("Error loading configuration: %s", str(e))
            return None
    else:
        print("No config file found.")
        print("Please make a configuration in the panel")
        return None



# Load the configuration
config = load_config()


socket_buffer_size = 1024
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
long_lived_access_token = config.get('long_lived_access_token')
debug_output = config.get('debug_output')


url = "http://homeassistant.local:8123/api/states/sensor.kitchen_temperature"
headers = {
    "Authorization": f"Bearer {long_lived_access_token}",
    "content-type": "application/json",
}
data = {"state": "125", "attributes": {"unit_of_measurement": "°C"}}
response = post(url, headers=headers, json=data)

print(response.text)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global mqtt_connected
        mqtt_connected = True
        client.will_set(mqtt_base_topic + "/availability","online", qos=0, retain=False)
        print(f"Connected to MQTT Broker: {mqtt_broker}:{mqtt_port}")
    else:
        client.will_set(mqtt_base_topic + "/availability","offline", qos=0, retain=True)
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
    if interface == 'serial' and serial_port and baud_rate:
        try:
            print("Trying to connect " + serial_port + ":" + str(baud_rate))
            ser = serial.Serial(serial_port, baud_rate, timeout = 1)
            print(f"Connected to BMS over serial port: {serial_port} with baud rate: {baud_rate}")
            return ser
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return None
    elif interface == 'ethernet' and ethernet_ip and ethernet_port:
        try:
            print("Trying to connect " + ethernet_ip + ":" + str(ethernet_port))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
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
        # Ensure data is in bytes format
        if isinstance(data, str):
            data = data.encode()  # Convert string to bytes if necessary

        # Check if the connection is a socket (Ethernet)
        if hasattr(bms_connection, 'send'):
            bms_connection.send(data)
        # Check if the connection is a serial connection
        elif hasattr(bms_connection, 'write'):
            bms_connection.write(data)
        else:
            raise ValueError("Unsupported connection type")

        return True

    except Exception as e:
        print(f"Error sending data to BMS: {e}")
        return False

def receive_data_from_bms(bms_connection):
    try:
        # Check if the connection is a serial connection
        if hasattr(bms_connection, 'readline'):
            received_data = bms_connection.readline().decode().strip()
        # Check if the connection is a socket (Ethernet)
        elif hasattr(bms_connection, 'recv'):
            # Assuming a buffer size of 1024 bytes for demonstration purposes
            received_data = bms_connection.recv(socket_buffer_size).decode().strip()
        else:
            raise ValueError("Unsupported connection type")

        print(f"Received data from BMS: {received_data}")
        return received_data
    except Exception as e:
        print(f"Error receiving data from BMS: {e}")
        return None





def lchksum_calc(lenid):
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

def chksum_calc(data):
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

def ha_discovery(client, data_payload):

    print("Publishing HA Discovery topic...")

    device = {
        'manufacturer': "Gobel",
        'model': "GP200",
        'identifiers': "Gobel-GP200",
        'name': "GP200",
        'sw_version': 1.1
    }

    combined_payload = [ {**data, 'device': device} for data in data_payload]

    # Convert the payload to JSON string
    json_payload = json.dumps(combined_payload)

    # Publish the JSON payload to the MQTT topic
    client.publish(config['mqtt_ha_discovery_topic'] + "/sensor/BMSconfig", json_payload, qos=0, retain=True)

def run():

    print(f"interface: {interface}")
    print(f"serial_port: {serial_port}")
    print(f"baud_rate: {baud_rate}")
    print(f"ethernet_ip: {ethernet_ip}")
    print(f"ethernet_port: {ethernet_port}")

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
                pacebms.get_capacity_data(bms_connection, pack_number=None)
                pacebms.get_time_date_data(bms_connection, pack_number=None)
                pacebms.get_product_info_data(bms_connection, pack_number=None)
                initial_data_fetched = True  # Set the flag to True after fetching initial data
            
            # Fetch analog and warning data every 5 seconds
            analog_data = pacebms.get_analog_data(bms_connection, pack_number=None)
            warning_data = pacebms.get_warning_data(bms_connection, pack_number=None)
            analog_topic = 'pacebms/analog'
            analog_topic = f"{mqtt_base_topic}/{analog_topic}"
            mqtt_client.publish(analog_topic, json.dumps(analog_data))
            print('analog data published to mqtt')
            warning_topic = 'pacebms/warning'
            warning_topic = f"{mqtt_base_topic}/{warning_topic}"
            mqtt_client.publish(warning_topic, json.dumps(warning_data))
            print('warning data published to mqtt')
            time.sleep(5)  # Sleep for 5 seconds between each iteration

    except KeyboardInterrupt:
        print("Stopping the program...")
    
    finally:
        mqtt_client.loop_stop()

if __name__ == "__main__":
    run()
