import requests
import const
import utils
import json

with open(const.DATA_NODES_PATH, 'r') as file:
    json_data = json.load(file)


def create_nodes():
    nodes = {}
    for index, node in enumerate(json_data):
        nodes[f'nodes[{index}][id]'] = node['id']
        nodes[f'nodes[{index}][type]'] = node['type']
    return nodes


class HDGBavariaAPI:
    def __init__(self, host: str):
        self.dataUrl = host + const.API_MANAGER_DATA_ENDPOINT
        self.nodes = create_nodes()

    def get_data(self):
        response = requests.post(self.dataUrl, params=self.nodes)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fehler beim Senden der Anfrage. Statuscode: {response.status_code}")
