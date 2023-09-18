import requests


class Requester:
    def __init__(self):
        self.base_url = "http://localhost:3000"

    def get(self, url, params=None, headers=None):
        full_url = self.base_url + url
        response = requests.get(full_url, params=params, headers=headers)
        return response.json()

    def post(self, url, data=None, json=None, headers=None):
        full_url = self.base_url + url
        response = requests.post(full_url, data=data, json=json, headers=headers)
        return response.json()
