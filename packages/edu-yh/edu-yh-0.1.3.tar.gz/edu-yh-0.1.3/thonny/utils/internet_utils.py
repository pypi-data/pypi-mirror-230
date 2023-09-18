import socket

"""
网络连接工具类
"""


class InternetUtil:
    def __init__(self):
        self.network_connections = False

    """
    检查网络连接状况
    """

    def check_internet_connection(self, host="180.76.235.69", port=3306, timeout=5):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            self.network_connections = True
            return self.network_connections
        except OSError:
            self.network_connections = False
            return self.network_connections
