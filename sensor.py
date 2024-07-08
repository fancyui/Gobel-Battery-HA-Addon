import paho.mqtt.client as mqtt
import time
import os
import json
import sys
import logging
from bms_comm import BMSCommunication
from pacebms import PACEBMS
from ha_rest_api import HA_REST_API
from ha_mqtt import HA_MQTT

# Define the load_config function
def load_config():
    config_path = '/data/options.json'
    if os.path.exists(config_path):
        print("Loading options.json")
        try:
            with open(config_path) as file:
                config = json.load(file)
                # print("Config: " + json.dumps(config))
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
device_name = config.get('device_name')
battery_manufacturer = config.get('battery_manufacturer')
battery_model = config.get('battery_model')
interface = config.get('connection_type')
battery_port = config.get('battery_port')
bms_brand = config.get('bms_brand')
ethernet_ip = config.get('bms_ip_address')
ethernet_port = config.get('bms_ip_port')
serial_port = config.get('bms_usb_port')
baud_rate = config.get('bms_baud_rate')
data_refresh_interval = config.get('data_refresh_interval')
debug = config.get('debug')
if_random = config.get('if_random')

device_nameprocessed = device_name.lower().replace(" ", "_")

device_info = {
    "identifiers": f"{device_nameprocessed}_{battery_manufacturer}_{battery_model}",
    "name": device_name,
    "manufacturer": battery_manufacturer,
    "model": battery_model,
    "sw_version": "1.0"
}

device_name = device_nameprocessed

# Configure logging
logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run():

    logger.info(f"interface: {interface}")
    logger.info(f"serial_port: {serial_port}")
    logger.info(f"baud_rate: {baud_rate}")
    logger.info(f"ethernet_ip: {ethernet_ip}")
    logger.info(f"ethernet_port: {ethernet_port}")


    # Connect to HA_REST_API
    # ha_comm = HA_REST_API(long_lived_access_token)
    # Connect to HA_MQTT
    ha_comm = HA_MQTT(mqtt_broker, mqtt_port, mqtt_username, mqtt_password, device_name, device_info, debug)
    mqtt_client = ha_comm.connect()
    if not mqtt_client:
        logger.info("HA Connection failed")
        return
    mqtt_client.loop_start()

    # Connect to BMS
    bms_comm = BMSCommunication(interface, serial_port, baud_rate, ethernet_ip, ethernet_port, buffer_size, debug)

    if not bms_comm.connect():
        logger.info("BMS Connection failed")
        return

    bms = PACEBMS(bms_comm, ha_comm, data_refresh_interval, debug, if_random)

    logger.info("Pace BMS Monitor Working...")

    initial_data_fetched = False  # Flag to track if initial data has been fetched

    try:
        while True:  # Run continuously
            if not initial_data_fetched:
                # Get initial data
                initial_data_fetched = True  # Set the flag to True after fetching initial data
            
            # Fetch analog and warning data every 5 seconds
            bms.publish_analog_data_mqtt()
            bms.publish_warning_data_mqtt()

            time.sleep(data_refresh_interval)  # Sleep for 5 seconds between each iteration

    except KeyboardInterrupt:
        logger.info("Stopping the program...")
    
    finally:
        mqtt_client.loop_stop()

if __name__ == "__main__":
    run()
