import paho.mqtt.client as mqtt
import json
import logging

class HA_MQTT:

    def __init__(self, mqtt_broker, mqtt_port, mqtt_user, mqtt_password, base_topic, device_info, debug):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.base_topic = base_topic
        self.device_info = device_info
        self.mqtt_client = None

        # Configure logging
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def cap_first(self,s):
        if not s:
            return s  # Return the empty string if input is empty
        return s[0].upper() + s[1:]

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

    def publish_sensor_discovery(self, entity_id, unit, icon):
        main_topic = 'sensor'
        topic = f"homeassistant/{main_topic}/{self.base_topic}_{entity_id}/config"
        self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": " ".join(self.cap_first(word) for word in entity_id.split("_")),
            "state_topic": f"{main_topic}/{self.base_topic}_{entity_id}/state",
            "unique_id": f"{self.base_topic}_{entity_id}",
            "unit_of_measurement": unit,
            "icon": icon,
            "value_template": "{{ value_json.state }}",
            "device": self.device_info
        }
        self.logger.debug(f"Discovery payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            self.logger.debug(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")

    def publish_sensor_state(self, value, unit, entity_id):
        main_topic = 'sensor'
        topic = f"{main_topic}/{self.base_topic}_{entity_id}/state"
        self.logger.debug(f"Publishing data to topic: {topic}")
        payload = {
            "state": value,
            "attributes": {"unit_of_measurement": unit}
        }
        self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            self.logger.debug(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")

    def publish_event_discovery(self, entity_id):
        main_topic = 'event'
        topic = f"homeassistant/{main_topic}/{self.base_topic}_{entity_id}/config"
        self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": " ".join(self.cap_first(word) for word in entity_id.split("_")),
            "state_topic": f"{main_topic}/{self.base_topic}_{entity_id}/state",
            "unique_id": f"{self.base_topic}_{entity_id}",
            "event_types": ["normal", 
                            "below lower limit", 
                            "above upper limit", 
                            "other fault", 
                            "unknown"
                            ],
            "icon":  "mdi:battery-heart-variant",
            "device": self.device_info
        }
        self.logger.debug(f"Discovery payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            self.logger.debug(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")


    def publish_event_state(self, value, entity_id):
        main_topic = 'event'
        topic = f"{main_topic}/{self.base_topic}_{entity_id}/state"
        self.logger.debug(f"Publishing data to topic: {topic}")
        payload = {
            "event_type": value
        }
        self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            self.logger.debug(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")

    def publish_binary_sensor_discovery(self, entity_id, icon):
        main_topic = 'binary_sensor'
        topic = f"homeassistant/{main_topic}/{self.base_topic}_{entity_id}/config"
        self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": " ".join(self.cap_first(word) for word in entity_id.split("_")),
            "state_topic": f"{main_topic}/{self.base_topic}_{entity_id}/state",
            "unique_id": f"{self.base_topic}_{entity_id}",
            "payload_on": True,
            "payload_off": False,
            "icon": icon,
            "value_template": "{{ value_json.state }}",
            "device": self.device_info
        }
        self.logger.debug(f"Discovery payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            self.logger.debug(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")


    def publish_binary_sensor_state(self, value, entity_id):
        main_topic = 'binary_sensor'
        topic = f"{main_topic}/{self.base_topic}_{entity_id}/state"
        self.logger.debug(f"Publishing data to topic: {topic}")
        payload = {
            "state": value
        }
        self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            self.logger.debug(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")


    def publish_warn_discovery(self, entity_id, icon):
        main_topic = 'sensor'
        topic = f"homeassistant/{main_topic}/{self.base_topic}_{entity_id}/config"
        self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": " ".join(self.cap_first(word) for word in entity_id.split("_")),
            "state_topic": f"{main_topic}/{self.base_topic}_{entity_id}/state",
            "unique_id": f"{self.base_topic}_{entity_id}",
            "icon": icon,
            "value_template": "{{ value_json.state }}",
            "device": self.device_info
        }
        self.logger.debug(f"Discovery payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            self.logger.debug(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")


    def publish_warn_state(self, value, entity_id):
        main_topic = 'sensor'
        topic = f"{main_topic}/{self.base_topic}_{entity_id}/state"
        self.logger.debug(f"Publishing data to topic: {topic}")

        payload = {
            "state": value,
        }

        self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            self.logger.debug(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")





