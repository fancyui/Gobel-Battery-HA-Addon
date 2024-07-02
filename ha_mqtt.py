import paho.mqtt.client as mqtt
import json
import logging

class HA_MQTT:

    def __init__(self, mqtt_broker, mqtt_port, mqtt_user, mqtt_password, base_topic, device_info):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.base_topic = base_topic
        self.device_info = device_info
        self.mqtt_client = None

        # Configure logging
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.logger.debug("Initializing MQTT client")
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)
        self.logger.info(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.logger.info("Connected to MQTT broker successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
        return self.mqtt_client

    def publish_discovery(self, entity_id, unit, device_class=None):
        topic = f"homeassistant/{self.base_topic}/gobel_{entity_id}/config"
        self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": entity_id,
            "state_topic": f"{self.base_topic}/gobel_{entity_id}/state",
            "unique_id": f"gobel_{entity_id}",
            "unit_of_measurement": unit,
            "device_class": device_class,
            "value_template": "{{ value_json.state }}",
            "device": self.device_info
        }
        self.logger.debug(f"Discovery payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            self.logger.info(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")

    def publish_data(self, value, unit, entity_id):
        topic = f"{self.base_topic}/gobel_{entity_id}/state"
        self.logger.debug(f"Publishing data to topic: {topic}")
        payload = {
            "state": value,
            "attributes": {"unit_of_measurement": unit}
        }
        self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            self.logger.info(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")

