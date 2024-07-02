import paho.mqtt.client as mqtt
import time
import os
import json
import sys
import logging
from bms_communication import BMSCommunication
from pacebms import PACEBMS
from ha_rest_api import HA_REST_API



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


buffer_size = 1024
# Accessing the parameters
mqtt_broker = config.get('mqtt_broker')
mqtt_port = config.get('mqtt_port')
mqtt_username = config.get('mqtt_username')
mqtt_password = config.get('mqtt_password')
mqtt_enable_discovery = config.get('mqtt_enable_discovery')
mqtt_discovery_topic = config.get('mqtt_discovery_topic')
base_topic = config.get('base_topic')
interface = config.get('connection_type')
bms_brand = config.get('bms_brand')
ethernet_ip = config.get('bms_ip_address')
ethernet_port = config.get('bms_ip_port')
serial_port = config.get('bms_usb_port')
baud_rate = config.get('bms_baud_rate')
data_refresh_interval = config.get('data_refresh_interval')
long_lived_access_token = config.get('long_lived_access_token')
debug_output = config.get('debug_output')


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

    client.publish(base_topic, data)
    print(f"Data sent to MQTT Broker: {data}")

    client.loop_stop()
    client.disconnect()


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


    # Connect to MQTT
    mqtt_client = setup_mqtt_client()
    mqtt_client.loop_start()
    # Connect to BMS
    bms_comm = BMSCommunication(interface, serial_port, baud_rate, ethernet_ip, ethernet_port, buffer_size)

    if not bms_comm.connect():
        print("Connection failed")
        return

    # Connect to HA_REST_API
    ha_rest_api = HA_REST_API(long_lived_access_token)

    bms = PACEBMS(bms_comm, ha_rest_api, base_topic)
    


    initial_data_fetched = False  # Flag to track if initial data has been fetched

    try:
        while True:  # Run continuously
            if not initial_data_fetched:
                # Get initial data
                bms.get_capacity_data(pack_number=None)
                bms.get_time_date_data(pack_number=None)
                bms.get_product_info_data(pack_number=None)
                initial_data_fetched = True  # Set the flag to True after fetching initial data
            
            # Fetch analog and warning data every 5 seconds
            analog_data = bms.get_analog_data(pack_number=None)
            bms.publish_analog_data()
            # warning_data = bms.get_warning_data(pack_number=None)
            # analog_topic = f"{bms_brand}/analog"
            # analog_topic = f"{base_topic}/{analog_topic}"
            # mqtt_client.publish(analog_topic, json.dumps(analog_data))
            # print('analog data published to mqtt')
            # warning_topic = f"{bms_brand}/warning"
            # warning_topic = f"{base_topic}/{warning_topic}"
            # mqtt_client.publish(warning_topic, json.dumps(warning_data))
            # print('warning data published to mqtt')

            time.sleep(5)  # Sleep for 5 seconds between each iteration

    except KeyboardInterrupt:
        print("Stopping the program...")
    
    finally:
        mqtt_client.loop_stop()

if __name__ == "__main__":
    run()
