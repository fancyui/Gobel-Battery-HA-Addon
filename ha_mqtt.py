import paho.mqtt.client as mqtt
import json

class HA_MQTT:

    def __init__(self, mqtt_broker, mqtt_port, mqtt_user, mqtt_password, base_topic):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.base_topic = base_topic
        self.device_info = device_info

    def connect(self):
        client = mqtt.Client()
        client.username_pw_set(self.mqtt_user, self.mqtt_password)
        client.connect(self.mqtt_broker, self.mqtt_port, 60)
        return client

    def publish_discovery(self, entity_id, name, unit, device_class=None):
        topic = f"homeassistant/sensor/{entity_id}/config"
        payload = {
            "name": name,
            "state_topic": f"{self.base_topic}/{entity_id}/state",
            "unit_of_measurement": unit,
            "device_class": device_class,
            "value_template": "{{ value_json.state }}",
            "device": self.device_info
        }
        self.client.publish(topic, json.dumps(payload), retain=True)

    def publish_data(self, value, unit, entity_id):
        topic = f"{self.base_topic}/{entity_id}/state"
        payload = {
            "state": value,
            "attributes": {"unit_of_measurement": unit}
        }
        self.client.publish(topic, json.dumps(payload))

