import socket


class User:
    def __init__(self, user_id=None, user_name=None, password=None, email=None, tcp_socket=None, udp_socket=None,
                 address=None, udp_port=None, tcp_port=None):
        self._user_id = user_id
        self._username = user_name
        self._password = password
        self._email = email
        self._tcp_socket = tcp_socket
        self._udp_socket = udp_socket # ВОЗМОЖНО НЕ НУЖНО
        self._udp_port = udp_port
        self._tcp_port = tcp_port
        self._address = address
        self._is_online = None  # Later
        self._is_muted = None  # Later
        self._is_deafened = None  # Later
        self._room = None  # Later

    def get_tcp_socket(self):
        return self._tcp_socket

    # ВОЗМОЖНО НЕ НУЖНО
    def get_udp_socket(self):
        return self._udp_socket

    def get_address(self):
        return self._address

    def get_user_id(self):
        return self._user_id
