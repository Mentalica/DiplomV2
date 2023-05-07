import socket


class User:
    def __init__(self, user_id=None, user_name=None, password=None, email=None, main_tcp_socket_client=None,
                 cmd_tcp_socket=None, udp_socket=None, address=None, screen_udp_port_client=None,
                 cmd_tcp_port_client=None, voice_udp_port_client=None, video_udp_port_client=None,
                 cmd_tcp_port_server=None, screen_udp_port_server=None, voice_udp_port_server=None,
                 video_udp_port_server=None, main_tcp_port=None):
        self._user_id = user_id
        self._username = user_name
        self._password = password
        self._email = email
        self._main_tcp_port = main_tcp_port
        self._address = address
        # server ports
        self._cmd_tcp_port_server = cmd_tcp_port_server
        self._screen_udp_port_server = screen_udp_port_server
        self._voice_udp_port_server = voice_udp_port_server
        self._video_udp_port_server = video_udp_port_server
        # client ports
        self._cmd_tcp_port_client = cmd_tcp_port_client
        self._screen_udp_port_client = screen_udp_port_client
        self._voice_udp_port_client = voice_udp_port_client
        self._video_udp_port_client = video_udp_port_client
        # server sockets
        # self._main_tcp_socket = main_tcp_socket
        self._cmd_tcp_socket_server = None
        self._screen_udp_socket_server = None
        self._voice_udp_socket_server = None
        self._video_udp_socket_server = None
        # client sockets
        self._main_tcp_socket_client = main_tcp_socket_client
        self._cmd_tcp_socket_client = None

        #Flags
        self._is_online = None  # Later
        self._is_muted = None  # Later
        self._is_deafened = None  # Later
        self._room = None  # Later



    # Геттеры

    @property
    def cmd_tcp_socket_client(self):
        return self._cmd_tcp_socket_client

    @property
    def address(self):
        return self._address

    @property
    def cmd_tcp_socket_server(self):
        return self._cmd_tcp_socket_server

    @property
    def screen_udp_socket_server(self):
        return self._screen_udp_socket_server

    @property
    def voice_udp_socket_server(self):
        return self._voice_udp_socket_server

    @property
    def video_udp_socket_server(self):
        return self._video_udp_socket_server

    @property
    def cmd_tcp_port_server(self):
        return self._cmd_tcp_port_server

    @property
    def screen_udp_port_server(self):
        return self._screen_udp_port_server

    @property
    def voice_udp_port_server(self):
        return self._voice_udp_port_server

    @property
    def video_udp_port_server(self):
        return self._video_udp_port_server

    @property
    def cmd_tcp_port_client(self):
        return self._cmd_tcp_port_client

    @property
    def screen_udp_port_client(self):
        return self._screen_udp_port_client

    @property
    def voice_udp_port_client(self):
        return self._voice_udp_port_client

    @property
    def video_udp_port_client(self):
        return self._video_udp_port_client

    @property
    def user_id(self):
        return self._user_id

    # Сеттеры

    @cmd_tcp_socket_client.setter
    def cmd_tcp_socket_client(self, value):
        self._cmd_tcp_socket_client = value
    @address.setter
    def address(self, new_address):
        self._address = new_address

    @cmd_tcp_socket_server.setter
    def cmd_tcp_socket_server(self, value):
        self._cmd_tcp_socket_server = value

    @screen_udp_socket_server.setter
    def screen_udp_socket_server(self, value):
        self._screen_udp_socket_server = value

    @voice_udp_socket_server.setter
    def voice_udp_socket_server(self, value):
        self._voice_udp_socket_server = value

    @video_udp_socket_server.setter
    def video_udp_socket_server(self, value):
        self._video_udp_socket_server = value

    @cmd_tcp_port_server.setter
    def cmd_tcp_port_server(self, value):
        self._cmd_tcp_port_server = value

    @screen_udp_port_server.setter
    def screen_udp_port_server(self, value):
        self._screen_udp_port_server = value

    @voice_udp_port_server.setter
    def voice_udp_port_server(self, value):
        self._voice_udp_port_server = value

    @video_udp_port_server.setter
    def video_udp_port_server(self, value):
        self._video_udp_port_server = value

    @cmd_tcp_port_client.setter
    def cmd_tcp_port_client(self, value):
        self._cmd_tcp_port_client = value

    @screen_udp_port_client.setter
    def screen_udp_port_client(self, value):
        self._screen_udp_port_client = value

    @voice_udp_port_client.setter
    def voice_udp_port_client(self, value):
        self._voice_udp_port_client = value

    @video_udp_port_client.setter
    def video_udp_port_client(self, value):
        self._video_udp_port_client = value

    @user_id.setter
    def user_id(self, value):
        self._user_id = value
