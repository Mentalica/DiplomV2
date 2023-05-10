import base64
import socket
import struct
import threading
import time
import zlib
from typing import List

import cv2
import numpy as np
import pyaudio

from messageType import MessageType
from message import Message
from networkManager import NetworkManager
from audioRecorder import AudioRecorder
from consts import *
from user import User
from room import Room


class Server:
    def __init__(self, max_client=MAX_CLIENTS_COUNT):
        self._is_tcp_connected = False
        self._is_udp_connected = False
        self._tcp_server_socket = None
        self._udp_server_socket = None
        self._max_clients = max_client
        self._is_audio_stream = False
        self._is_video_stream = False
        self._is_screen_stream = False
        self._rooms: List[Room] = []
        self._clients: list[User] = []

    def start(self):
        self._tcp_server_socket = self.create_tcp_socket(MAIN_TCP_SERVER_PORT, self._max_clients)
        # self.create_udp_socket()

    def stop(self):
        self.close_tcp_server_connection()
        self.close_udp_server_connection()

    def create_udp_socket(self, udp_server_port):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((MAIN_SERVER_ADDRESS, udp_server_port))
        # self._is_udp_connected = True
        print(f"[OK] {SERVER} UDP server started at {MAIN_SERVER_ADDRESS}:{udp_server_port}\n\tSocket: "
              f"{udp_socket}")
        return udp_socket

    def create_tcp_socket(self, tcp_server_port, max_clients=1):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.bind((MAIN_SERVER_ADDRESS, tcp_server_port))
        tcp_socket.listen(max_clients)
        # self._is_tcp_connected = True
        print(f"[OK] {SERVER} TCP server started at {MAIN_SERVER_ADDRESS}:{tcp_server_port}\n\tSocket: "
              f"{tcp_socket}")
        return tcp_socket

    def close_udp_server_connection(self):
        self._udp_server_socket.close()
        # self._is_udp_connected = False
        print(f"[OK] {SERVER} UDP server was stopped")

    def close_tcp_server_connection(self):
        self._tcp_server_socket.close()
        # self._is_tcp_connected = False
        print(f"[OK] {SERVER} TCP server was stopped")

    def accept_connection(self):
        client_id = 0
        curr_port = FIRST_PORT
        stop_port = LAST_PORT
        while True:
            # Wait for a client to connect
            client_socket, client_address = self._tcp_server_socket.accept()
            print(f"[OK] {SERVER} TCP connection from {client_address} has been established! Client ID - {client_id}")
            new_client = User(user_id=client_id, main_tcp_socket_client=client_socket, address=client_address[0])

            # Создания сокетов сервера для клиента
            # client TCP server
            tcp_client_port = curr_port
            tcp_cmd_socket = self.create_tcp_socket(tcp_client_port)
            new_client.cmd_tcp_port_server = tcp_cmd_socket
            new_client.cmd_tcp_port_server = tcp_client_port
            # client screen UDP server
            curr_port += 1
            udp_screen_port = curr_port
            new_client.screen_udp_socket_server = self.create_udp_socket(udp_screen_port)
            # udp_screen_socket = self.create_udp_socket(udp_screen_port)
            new_client.screen_udp_port_server = udp_screen_port
            # client voice UDP server
            curr_port += 1
            udp_voice_port = curr_port
            new_client.voice_udp_socket_server = self.create_udp_socket(udp_voice_port)
            # udp_voice_socket = self.create_udp_socket(udp_voice_port)
            new_client.voice_udp_port_server = udp_voice_port
            # client video UDP server
            curr_port += 1
            udp_video_port = curr_port
            new_client.video_udp_socket_server = self.create_udp_socket(udp_video_port)
            # udp_video_socket = self.create_udp_socket(udp_video_port)
            new_client.video_udp_port_server = udp_video_port
            data_to_send = "|".join([str(tcp_client_port), str(udp_screen_port), str(udp_voice_port),
                                     str(udp_video_port)])
            print(f"[smg to send] {SERVER}: ({type(data_to_send)}) {data_to_send}")
            # Send available ports
            Message.send_message_tcp(client_socket, MessageType.ECHO, data_to_send.encode())

            # Подключение клиента к сокетам сервера
            # client TCP server
            client_socket_cmd, client_address_cmd = tcp_cmd_socket.accept()
            print(f"[OK] {SERVER} TCP connection from {client_address} has been established! Client ID - {client_id}")
            new_client.cmd_tcp_port_client = client_address_cmd[1]
            new_client.cmd_tcp_socket_client = client_socket_cmd
            new_client.cmd_tcp_socket = client_socket_cmd

            # client screen UDP server
            screen_udp_msg = Message.receive_message_udp(new_client.screen_udp_socket_server)
            if int(screen_udp_msg[0]) == MessageType.ECHO and screen_udp_msg[1].decode() == "OK":
                new_client.screen_udp_port_client = screen_udp_msg[2][1]
                print(f"[OK] {SERVER} UDP Screen connection from {screen_udp_msg[2]} has been established! Client ID "
                      f"- {client_id}")
                Message.send_message_udp(new_client.screen_udp_socket_server, MessageType.ECHO, b"OK",
                                         new_client.address, new_client.screen_udp_port_client)
            else:
                print(f"[ERROR] {SERVER}: {screen_udp_msg[0]}\n{screen_udp_msg[1]}")

            # client voice UDP server
            voice_udp_msg = Message.receive_message_udp(new_client.voice_udp_socket_server)
            if int(voice_udp_msg[0]) == MessageType.ECHO and voice_udp_msg[1].decode() == "OK":
                new_client.voice_udp_port_client = voice_udp_msg[2][1]
                print(f"[OK] {SERVER} UDP Voice connection from {voice_udp_msg[2]} has been established! Client ID "
                      f"- {client_id}")
                Message.send_message_udp(new_client.voice_udp_socket_server, MessageType.ECHO, b"OK",
                                         new_client.address, new_client.voice_udp_port_client)
            else:
                print(f"[ERROR] {SERVER}: {voice_udp_msg[0]}\n{voice_udp_msg[1]}")

            # client video UDP server
            video_udp_msg = Message.receive_message_udp(new_client.video_udp_socket_server)
            if int(video_udp_msg[0]) == MessageType.ECHO and video_udp_msg[1].decode() == "OK":
                new_client.video_udp_port_client = video_udp_msg[2][1]
                print(f"[OK] {SERVER} UDP video connection from {video_udp_msg[2]} has been established! Client ID "
                      f"- {client_id}")
                Message.send_message_udp(new_client.video_udp_socket_server, MessageType.ECHO, b"OK",
                                         new_client.address, new_client.video_udp_port_client)
            else:
                print(f"[ERROR] {SERVER}: {video_udp_msg[0]}\n{video_udp_msg[1]}")

            # Add user in list

            self._clients.append(new_client)
            client_thread = threading.Thread(target=self.handle_client, args=(new_client,))
            client_id += 1
            client_thread.start()

    def handle_client(self, client: User):
        while True:
            # Принимаем сообщение от клиента
            message_type, message_data = Message.receive_message_tcp(client.cmd_tcp_socket_client)
            print(f"[RECEIVED] {SERVER}: msg_type - {message_type}; client ID - {client.user_id}"
                  f"\n\tmsg_data: {message_data.decode()}")
            # if client.active_room:
            # Обрабатываем сообщение в зависимости от его типа
            if message_type == MessageType.ECHO:
                threading.Thread(target=Message.send_message_tcp,
                                 args=(client.cmd_tcp_socket_client, MessageType.ECHO, b"Hello there",)).start()
            elif message_type == MessageType.VIDEO:
                if message_data == START_FLAG:
                    client.is_video_stream = True
                    threading.Thread(target=self.video_handler, args=(client,)).start()
                elif message_data == STOP_FLAG:
                    client.is_video_stream = False
            elif message_type == MessageType.AUDIO:
                if message_data == START_FLAG:
                    client.is_voice_stream = True
                    threading.Thread(target=self.audio_handler, args=(client,)).start()
                elif message_data == STOP_FLAG:
                    client.is_voice_stream = False
            elif message_type == MessageType.SCREENSHARE:
                if message_data == START_FLAG:
                    client.is_screen_stream = True
                    threading.Thread(target=self.screenshare_handler, args=(client,)).start()
                elif message_data == STOP_FLAG:
                    client.is_screen_stream = False
            elif message_type == MessageType.CREATE_ROOM:
                self.create_room(message_data, client)
            elif message_type == MessageType.DELETE_ROOM:
                self.delete_room(message_data, client)
            elif message_type == MessageType.JOIN_ROOM:
                self.join_room(message_data, client)
            elif message_type == MessageType.LEAVE_ROOM:
                client.active_room = None
            elif message_type == MessageType.GET_ROOM_LIST:
                self.get_room_list(client)
            elif message_type == MessageType.GET_CLIENT_LIST:
                self.get_client_list(client)

    def get_client_list(self, client: User):
        if client.active_room:

            msg = "|".join([user.username for user in client.active_room.get_user_list()])
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.GET_CLIENT_LIST, msg.encode())
        else:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.GET_CLIENT_LIST, ERROR_FLAG)

    def get_room_list(self, client: User):
        # print([user.user_id for user in client.active_room.get_user_list()])
        print([room.room_name for room in client.get_room_list()])
        msg = "|".join([room.room_name for room in client.get_room_list()])
        Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.GET_ROOM_LIST, msg.encode())

    def create_room(self, message_data, client: User):
        room = self.find_room_by_name(message_data.decode())
        if room:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.CREATE_ROOM, ERROR_FLAG)
            return
        if len(self._rooms) == 0:
            room_id = 0
        else:
            room_id = self._rooms[-1].room_id
        room = Room(room_id=room_id, room_name=message_data.decode(), owner=client)
        self._rooms.append(room)
        client.active_room = room
        # room.add_user_to_room(client)
        Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.CREATE_ROOM, OK_FLAG+b"|"+message_data)

    def delete_room(self, message_data, client: User):
        if client.active_room.room_name == message_data.decode():
            room = self.find_room_by_id(client.active_room.room_id)
            if room and room.is_owner(client):
                room.delete_room_for_users()
                self._rooms.remove(room)
                Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.DELETE_ROOM, OK_FLAG+b"|"+message_data)
            else:
                Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.DELETE_ROOM, ERROR_FLAG)
        else:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.DELETE_ROOM, ERROR_FLAG)

    def join_room(self, message_data, client: User):
        room = self.find_room_by_name(message_data.decode())
        if room:
            room.add_user_to_room(client)
            client.active_room = room
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.JOIN_ROOM, OK_FLAG+b"|"+message_data)
            # ОТПРАВЛЯТЬ СООБЩЕНИЯ ДЛЯ СТАРТА СТРИМОВ
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.AUDIO, START_FLAG)
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.VIDEO, START_FLAG)
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.SCREENSHARE, START_FLAG)
        else:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.JOIN_ROOM, ERROR_FLAG)

    def find_room_by_id(self, room_id):
        for room in self._rooms:
            if room.room_id == room_id:
                return room
        return None

    def find_room_by_name(self, room_name):
        for room in self._rooms:
            if room.room_name == room_name:
                return room
        return None

    # def screenshare_handler(self, client: User):
    #     while self._is_screen_stream:
    #         data = Message.receive_large_message_udp(client.screen_udp_socket_server)
    #         # data = Message.recv_large_message_udp(client.screen_udp_socket_server)
    #         if data[0] == MessageType.SCREENSHARE:
    #             frame = cv2.imdecode(np.frombuffer(data[1], dtype=np.uint8), cv2.IMREAD_COLOR)
    #
    #             cv2.imshow('Video Frame', frame)
    #             if cv2.waitKey(1) == ord('q'):
    #                 Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.SCREENSHARE, STOP_FLAG)
    #                 break
    #     cv2.destroyAllWindows()

    def screenshare_handler(self, client: User):
        for user in client.active_room.get_user_list():
            Message.send_message_tcp(user.cmd_tcp_socket_client, MessageType.SCREENSHARE, START_FLAG)
        while client.is_screen_stream:
            data = Message.receive_large_message_udp(client.screen_udp_socket_server)
            # data = Message.recv_large_message_udp(client.screen_udp_socket_server)
            for user in client.active_room.get_user_list():
                # print(f"Sended to - {user}")
                # print(f"data - {data}")
                if client.user_id != user.user_id:
                    threading.Thread(target=Message.send_large_message_udp, args=(user.screen_udp_socket_server,
                                                                                  MessageType.SCREENSHARE, data[1],
                                                                                  user.address,
                                                                                  user.screen_udp_port_client,)).start()
        for user in client.active_room.get_user_list():
            Message.send_message_tcp(user.cmd_tcp_socket_client, MessageType.SCREENSHARE, STOP_FLAG)

    def audio_handler(self, client: User):
        # audio = AudioRecorder()
        # audio.out_stream_audio()
        # while client.is_voice_stream:
        #     data = Message.receive_message_udp(client.voice_udp_socket_server)
        #     if data[0] == MessageType.AUDIO:
        #         # print(f"[AUDIO_HANDLER] {SERVER}: {data}")
        #         data = zlib.decompress(data[1])
        #         # Проигрываем декодированное аудио
        #         audio.stream.write(data)
        # audio.close()

        for user in client.active_room.get_user_list():
            Message.send_message_tcp(user.cmd_tcp_socket_client, MessageType.AUDIO, START_FLAG)
        while client.is_voice_stream:
            data = Message.receive_message_udp(client.voice_udp_socket_server)
            i = 0
            for user in client.active_room.get_user_list():
                print(f"Users: - {i}")
                i += 1

                if client.user_id != user.user_id:

                    threading.Thread(target=Message.send_message_udp, args=(user.voice_udp_socket_server,
                                                                            MessageType.AUDIO, data[1], user.address,
                                                                            user.voice_udp_port_client,)).start()
        for user in client.active_room.get_user_list():
            Message.send_message_tcp(user.cmd_tcp_socket_client, MessageType.AUDIO, STOP_FLAG)

    def video_handler(self, client: User):
        # while self._is_video_stream:
        #     # data = Message.receive_message_udp(client.video_udp_socket_server)
        #     data = Message.receive_large_message_udp(client.video_udp_socket_server)
        #     # print(f"{len(data[1])}\ndata: {data[1]}")
        #     if data[0] == MessageType.VIDEO:
        #         frame = cv2.imdecode(np.frombuffer(data[1], dtype=np.uint8), cv2.IMREAD_COLOR)
        #
        #         # print(frame)
        #         cv2.imshow('Video Frame', frame)
        #         if cv2.waitKey(1) == ord('q'):
        #             Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.VIDEO, STOP_FLAG)
        #             break
        # cv2.destroyAllWindows()

        for user in client.active_room.get_user_list():
            Message.send_message_tcp(user.cmd_tcp_socket_client, MessageType.VIDEO, START_FLAG)
        while client.is_video_stream:
            data = Message.receive_large_message_udp(client.video_udp_socket_server)
            for user in client.active_room.get_user_list():
                if client.user_id != user.user_id:
                    threading.Thread(target=Message.send_large_message_udp, args=(user.video_udp_socket_server,
                                                                                  MessageType.VIDEO, data[1],
                                                                                  user.address,
                                                                                  user.video_udp_port_client,)).start()
        for user in client.active_room.get_user_list():
            Message.send_message_tcp(user.cmd_tcp_socket_client, MessageType.VIDEO, STOP_FLAG)

    def broadcast_message(self):
        pass

    def get_all_rooms(self):
        pass
