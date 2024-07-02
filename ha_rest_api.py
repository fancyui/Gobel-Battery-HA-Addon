import requests

class HA_REST_API:

    def __init__(self,long_lived_access_token):
        self.long_lived_access_token = long_lived_access_token

    def publish_data(self, value, unit, entity_id):

        base_url = "http://homeassistant.local:8123/api/states/"
        headers = {
            "Authorization": f"Bearer {self.long_lived_access_token}",
            "content-type": "application/json",
        }

        data = {
            "state": value,
            "attributes": {"unit_of_measurement": unit}
        }

        url = base_url + entity_id
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            print(f"Error sending data for {entity_id}: {response.text}")