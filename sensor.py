import paho.mqtt.client as mqtt
import time
import os
import json
import sys
import logging
import threading
from bms_comm import BMSCommunication
from pacebms_rs232 import PACEBMS232
from pacebms_rs485 import PACEBMS485
from tdtbms_rs232 import TDTBMS232
from jkbms_rs485 import JKBMS485
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
host_name = config.get('host_name')
mqtt_discovery_topic = config.get('mqtt_discovery_topic')
device_name = config.get('device_name')
battery_manufacturer = config.get('battery_manufacturer')
battery_model = config.get('battery_model')
max_parallel_allowed = config.get('max_parallel_allowed')
interface = config.get('connection_type')
battery_port = config.get('battery_port')
bms_type = config.get('bms_type')
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

# Declare bms_comm in the global scope
bms_comm = None

def initiate_bms_communication():
    global bms_comm
    bms_comm = BMSCommunication(interface, serial_port, baud_rate, ethernet_ip, ethernet_port, buffer_size, debug)
    return bms_comm.connect()

def schedule_bms_reinit():
    initiate_bms_communication()
    # threading.Timer(60, schedule_bms_reinit).start()
    # logger.info(f"schedule_bms_reinit start")

def run():

    logger.info(f"interface: {interface}")
    logger.info(f"serial_port: {serial_port}")
    logger.info(f"baud_rate: {baud_rate}")
    logger.info(f"ethernet_ip: {ethernet_ip}")
    logger.info(f"ethernet_port: {ethernet_port}")


    # Connect to HA_REST_API
    # ha_comm = HA_REST_API(long_lived_access_token)
    # Connect to HA_MQTT
    ha_comm = HA_MQTT(mqtt_broker, mqtt_port, mqtt_username, mqtt_password, host_name, device_name, device_info, debug)
    mqtt_client = ha_comm.connect()
    if not mqtt_client:
        logger.info("HA Connection failed")
        return
    mqtt_client.loop_start()

    # Schedule the BMS re-initialization
    schedule_bms_reinit()

    if not bms_comm.connect():
        logger.info("BMS Connection failed")
        return

    if bms_type == 'PACE_LV':

        if battery_port == 'rs232':

            bms = PACEBMS232(bms_comm, ha_comm, bms_type, data_refresh_interval, debug, if_random)

            logger.info("PACE_LV BMS Monitor Working...")

            logger.info("PACE_LV BMS RS232 Working...")

            try:
                while True:  # Run continuously
                    
                    # Fetch analog and warning data every 5 seconds
                    bms.publish_analog_data_mqtt()
                    time.sleep(1)
                    bms.publish_warning_data_mqtt()

                    time.sleep(data_refresh_interval)  # Sleep for 5 seconds between each iteration

            except KeyboardInterrupt:
                logger.info("Stopping the program...")
            
            finally:
                mqtt_client.loop_stop()


        if battery_port == 'rs485':

            bms = PACEBMS485(bms_comm, ha_comm, data_refresh_interval, debug, if_random)

            logger.info("PACE_LV BMS Monitor Working...")

            logger.info("PACE_LV BMS RS485 Working...")

            logger.info("Looking for valid packs...")

            pack_list = []

            for pack_number in range(0, max_parallel_allowed+1):  #up to max_parallel_allowed
                result = bms.get_pack_num_data(pack_number)
                logger.debug(f"pack_number {result}")
                if result == pack_number:
                    pack_list.append(pack_number)

            logger.info(f"Found packs list: {pack_list}")
            
            if len(pack_list) > 0:

                try:
                    while True:  # Run continuously

                        bms.publish_analog_data_mqtt(pack_list)
                        time.sleep(1)
                        bms.publish_warning_data_mqtt(pack_list)
                    
                        time.sleep(data_refresh_interval)  # Sleep for 5 seconds between each iteration

                except KeyboardInterrupt:
                    logger.info("Stopping the program...")
                
                finally:
                    mqtt_client.loop_stop()

    elif bms_type == 'JK_PB':

        if battery_port == 'rs485':

            bms = JKBMS485(
                bms_comm=bms_comm,
                ha_comm=ha_comm,
                bms_type=bms_type,
                data_refresh_interval=data_refresh_interval,
                debug=debug,
                if_random=if_random
            )

            logger.info("JK_PB BMS Monitor Working...")
            logger.info("JK_PB BMS RS485 Working...")

            try:
                while True:  # Run continuously
                    
                    bms.publish_analog_data_mqtt()
                    time.sleep(1)
                    bms.publish_warning_data_mqtt()

                    time.sleep(data_refresh_interval)

            except KeyboardInterrupt:
                logger.info("Stopping the program...")
            
            finally:
                mqtt_client.loop_stop()
        
        else:
            logger.error(f"Unsupported port '{battery_port}' for JK_PB BMS. Only 'rs485' is supported.")

    elif bms_type == 'TDT':

        if battery_port == 'rs232':

            bms = TDTBMS232(bms_comm, ha_comm, data_refresh_interval, debug, if_random)

            logger.info("TDT BMS Monitor Working...")

            logger.info("TDT BMS RS232 Working...")

            logger.info("Looking for valid packs...")

            pack_list = []

            pack_quantity = bms.get_pack_quantity_data()

            pack_list = list(range(1, pack_quantity + 1))

            logger.info(f"Found packs list: {pack_list}")
            
            if len(pack_list) > 0:

                try:
                    while True:  # Run continuously

                        bms.publish_analog_data_mqtt(pack_list)
                        bms.publish_warning_data_mqtt(pack_list)
                    
                        time.sleep(data_refresh_interval)  # Sleep for 5 seconds between each iteration

                except KeyboardInterrupt:
                    logger.info("Stopping the program...")
                
                finally:
                    mqtt_client.loop_stop()

        if battery_port == 'rs485':
            logger.info("Please use RS232")

if __name__ == "__main__":
    run()
