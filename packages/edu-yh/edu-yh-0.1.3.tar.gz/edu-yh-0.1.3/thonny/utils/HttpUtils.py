import requests


class HttpUtil:
    @staticmethod
    def post(url, headers=None):
        response = requests.post(url, headers=headers)
        return response

    @staticmethod
    def post(url, headers=None, data=None):
        response = requests.post(url, headers=headers, data=data)
        return response

    @staticmethod
    def post(url, headers=None, data=None, file=None):
        response = requests.post(url, headers=headers, data=data, files=file)
        return response

    @staticmethod
    def get(url, headers=None):
        response = requests.get(url, headers=headers)
        return response

    @staticmethod
    def get(url, headers=None, params=None):
        response = requests.get(url, headers=headers, params=params)
        return response

    @staticmethod
    def delete(url, headers=None, params=None):
        response = requests.delete(url, headers=headers, params=params)
        return response
