import paho.mqtt.client as mqtt
import json
import logging

class HA_MQTT:

    def __init__(self, mqtt_broker, mqtt_port, mqtt_user, mqtt_password, host_name, device_name, device_info, debug):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.host_name = host_name
        self.device_name = device_name
        self.device_info = device_info
        self.mqtt_client = None

        # Configure logging
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def update_device_info(self, new_device_info):
        """
        Updates the device_info parameter with new information.

        :param new_device_info: The new device information to update with.
        """
        self.device_info = new_device_info
        self.logger.debug(f"Updated device_info to: {new_device_info}")

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

    def publish_sensor_discovery(self, entity_id, unit, icon, deviceclass, stateclass):
        main_topic = 'sensor'
        topic = f"{self.host_name}/{main_topic}/{self.device_name}_{entity_id}/config"
        # self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": " ".join(self.cap_first(word) for word in entity_id.split("_")),
            "state_topic": f"{main_topic}/{self.device_name}_{entity_id}/state",
            "unique_id": f"{self.device_name}_{entity_id}",
            "unit_of_measurement": unit,
            "icon": icon,
            "state_class": stateclass,
            # "suggested_display_precision": 2,
            "value_template": "{{ value_json.state }}",
            "device": self.device_info
        }
        if deviceclass != 'null':
            payload["device_class"] = deviceclass
        # self.logger.debug(f"Discovery payload: {json.dumps(payload)}")

        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            # self.logger.debug(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")

    def publish_sensor_state(self, value, unit, entity_id):
        main_topic = 'sensor'
        topic = f"{main_topic}/{self.device_name}_{entity_id}/state"
        # self.logger.debug(f"Publishing data to topic: {topic}")
        payload = {
            "state": value,
            "attributes": {"unit_of_measurement": unit}
        }
        # self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            # self.logger.debug(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")

    def publish_event_discovery(self, entity_id):
        main_topic = 'event'
        topic = f"{self.host_name}/{main_topic}/{self.device_name}_{entity_id}/config"
        # self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": " ".join(self.cap_first(word) for word in entity_id.split("_")),
            "state_topic": f"{main_topic}/{self.device_name}_{entity_id}/state",
            "unique_id": f"{self.device_name}_{entity_id}",
            "event_types": ["normal", 
                            "below lower limit", 
                            "above upper limit", 
                            "other fault", 
                            "unknown"
                            ],
            "icon":  "mdi:battery-heart-variant",
            "device": self.device_info
        }
        # self.logger.debug(f"Discovery payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            # self.logger.debug(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")


    def publish_event_state(self, value, entity_id):
        main_topic = 'event'
        topic = f"{main_topic}/{self.device_name}_{entity_id}/state"
        # self.logger.debug(f"Publishing data to topic: {topic}")
        payload = {
            "event_type": value
        }
        # self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            # self.logger.debug(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")

    def publish_binary_sensor_discovery(self, entity_id, icon):
        main_topic = 'binary_sensor'
        topic = f"{self.host_name}/{main_topic}/{self.device_name}_{entity_id}/config"
        # self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": " ".join(self.cap_first(word) for word in entity_id.split("_")),
            "state_topic": f"{main_topic}/{self.device_name}_{entity_id}/state",
            "unique_id": f"{self.device_name}_{entity_id}",
            "payload_on": True,
            "payload_off": False,
            "icon": icon,
            "value_template": "{{ value_json.state }}",
            "device": self.device_info
        }
        # self.logger.debug(f"Discovery payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            # self.logger.debug(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")


    def publish_binary_sensor_state(self, value, entity_id):
        main_topic = 'binary_sensor'
        topic = f"{main_topic}/{self.device_name}_{entity_id}/state"
        # self.logger.debug(f"Publishing data to topic: {topic}")
        payload = {
            "state": value
        }
        # self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            # self.logger.debug(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")


    def publish_warn_discovery(self, entity_id, icon):
        main_topic = 'sensor'
        topic = f"{self.host_name}/{main_topic}/{self.device_name}_{entity_id}/config"
        # self.logger.debug(f"Publishing discovery to topic: {topic}")
        payload = {
            "name": " ".join(self.cap_first(word) for word in entity_id.split("_")),
            "state_topic": f"{main_topic}/{self.device_name}_{entity_id}/state",
            "unique_id": f"{self.device_name}_{entity_id}",
            "icon": icon,
            "value_template": "{{ value_json.state }}",
            "device": self.device_info
        }
        # self.logger.debug(f"Discovery payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload), retain=True)
            # self.logger.debug(f"Published discovery for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish discovery for {topic}: {e}")


    def publish_warn_state(self, value, entity_id):
        main_topic = 'sensor'
        topic = f"{main_topic}/{self.device_name}_{entity_id}/state"
        # self.logger.debug(f"Publishing data to topic: {topic}")

        payload = {
            "state": value,
        }

        # self.logger.debug(f"Data payload: {json.dumps(payload)}")
        try:
            self.mqtt_client.publish(topic, json.dumps(payload))
            # self.logger.debug(f"Published data for {topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish data for {topic}: {e}")

