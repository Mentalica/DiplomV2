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
from audioRecorder import AudioRecorder
from consts import *
from networkManager import NetworkManager
from room import Room
from user import User
from chat import Chat, ChatMessage


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
        self._clients: List[NetworkManager] = []
        self._users: List[User] = []
        self._chats: List[Chat] = []

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
        while curr_port < stop_port:
            # Wait for a client to connect
            client_socket, client_address = self._tcp_server_socket.accept()
            print(f"[OK] {SERVER} TCP connection from {client_address} has been established! Client ID - {client_id}")
            new_client = NetworkManager(network_manager_id=client_id, main_tcp_socket_client=client_socket,
                                        address=client_address[0])

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

    def handle_client(self, client: NetworkManager):
        while True:
            # Принимаем сообщение от клиента
            message_type, message_data = Message.receive_message_tcp(client.cmd_tcp_socket_client)
            # if client.active_room:
            # Обрабатываем сообщение в зависимости от его типа
            print(f"[RECEIVED] {SERVER}: msg_type - {message_type}; client ID - {client.network_manager_id}; "
                  f"user ID - {client.user}\n\tmsg_data: {message_data.decode()}")
            if not client.user:
                if message_type == MessageType.CREATE_USER:
                    self.create_user(message_data, client)
                    continue
                elif message_type == MessageType.LOGIN_USER:
                    self.login_user(message_data, client)
                    continue
                else:
                    Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.ECHO, b"Please, Log In")
                    continue

            # print(f"[RECEIVED] {SERVER}: msg_type - {message_type}; client ID - {client.network_manager_id}; "
            #       f"user ID - {client.user.user_id}\n\tmsg_data: {message_data.decode()}")

            if message_type == MessageType.ECHO:
                threading.Thread(target=Message.send_message_tcp,
                                 args=(client.cmd_tcp_socket_client, MessageType.ECHO, b"Hello there",)).start()
            elif message_type == MessageType.VIDEO:
                if message_data == START_FLAG:
                    client.user.is_video_stream = True
                    threading.Thread(target=self.video_handler, args=(client,)).start()
                elif message_data == STOP_FLAG:
                    client.user.is_video_stream = False
            elif message_type == MessageType.AUDIO:
                if message_data == START_FLAG:
                    client.user.is_voice_stream = True
                    threading.Thread(target=self.audio_handler, args=(client,)).start()
                elif message_data == STOP_FLAG:
                    client.user.is_voice_stream = False
            elif message_type == MessageType.SCREENSHARE:
                if message_data == START_FLAG:
                    client.user.is_screen_stream = True
                    threading.Thread(target=self.screenshare_handler, args=(client,)).start()
                elif message_data == STOP_FLAG:
                    client.user.is_screen_stream = False
            elif message_type == MessageType.CREATE_ROOM:
                self.create_room(message_data, client)
            elif message_type == MessageType.DELETE_ROOM:
                self.delete_room(message_data, client)
            elif message_type == MessageType.JOIN_ROOM:
                self.join_room(message_data, client)
            elif message_type == MessageType.LEAVE_ROOM:
                client.user.active_room = None
            elif message_type == MessageType.GET_ROOM_LIST:
                self.get_room_list(client)
            elif message_type == MessageType.GET_CLIENT_LIST:
                self.get_client_list(client)
            elif message_type == MessageType.LOGOUT_USER:
                self.logout_user(message_data, client)
            elif message_type == MessageType.CHAT:
                self.handle_chat(message_data, client)
            elif message_type == MessageType.UPDATE_CHAT:
                self.update_user_chat(client)
            else:
                print(f"[RECEIVED] {SERVER} msg_type - {message_type}. Wrong command")

    def get_new_chat_id(self):
        if len(self._chats) == 0:
            return 0
        else:
            return self._chats[-1].chat_id + 1

    def create_chat(self, room):
        chat = Chat(self.get_new_chat_id(), room)
        room.chat = chat
        chat.room = room
        self._chats.append(chat)
        print(f"[CHAT-created] {SERVER} room_id - {chat.chat_id}")
        return chat

    def handle_chat(self, message_data,  client: NetworkManager):
        # if client.user.active_room.chat:
        chat = client.user.active_room.chat
        # else:
        #     chat = self.create_chat(client.user.active_room)
        chat_msg = ChatMessage(chat_message_id=chat.get_msg_chat_id(), message=message_data.decode(), user=client.user)
        chat.add_message_to_chat(chat_msg)
        msg_to_send = "|".join(chat_msg.get_info_list())
        for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
            print(cl)
            threading.Thread(target=Message.send_message_tcp, args=(cl.cmd_tcp_socket_client,
                                                                    MessageType.CHAT, msg_to_send.encode(),)).start()

    def update_user_chat(self, client: NetworkManager):
        Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.UPDATE_CHAT, START_FLAG)
        room = client.user.active_room
        print(f"ACTIVE ROOM FOR CLIENT")
        msgs = room.chat.get_chat_messages()
        print(f"msgs len - {len(msgs)}")
        for msg in msgs:
            print(f"msg - {msg}. MSG TO SEND -")
            msg_to_send = "|".join(msg.get_info_list())
            print(msg_to_send)
            threading.Thread(target=Message.send_message_tcp,
                             args=(client.cmd_tcp_socket_client, MessageType.UPDATE_CHAT,
                                   msg_to_send.encode(),)).start()
        Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.UPDATE_CHAT, STOP_FLAG)

    def create_user(self, message_data, client: NetworkManager):
        msg = message_data.decode().split("|")
        user = self.find_user_by_email(msg[0])
        if user and msg[0] and msg[1] and msg[2]:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.CREATE_USER, ERROR_FLAG)
            return
        if len(self._users) == 0:
            user_id = 0
        else:
            user_id = self._users[-1].user_id + 1
        user = User(user_id=user_id, email=msg[0], password=msg[1], username=msg[2], active_client=client)
        self._users.append(user)
        client.user = user
        user.is_online = True
        msg_to_send = "|".join([user.email, user.password, user.username])
        Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.CREATE_USER,
                                 OK_FLAG + b'|' + msg_to_send.encode())
    def find_user_by_email(self, email):
        for user in self._users:
            if user.email == email:
                return user
        return None

    def find_room_by_name(self, room_name):
        for room in self._rooms:
            if room.room_name == room_name:
                return room
        return None

    def login_user(self, message_data, client: NetworkManager):
        msg = message_data.decode().split("|")
        user = self.find_user_by_email(msg[0])
        if user and user.password == msg[1] and not user.is_online:
            msg_to_send = "|".join([user.email, user.password, user.username])
            client.user = user
            user.active_client = client
            user.is_online = True
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.LOGIN_USER,
                                     OK_FLAG + b'|' + msg_to_send.encode())
        else:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.LOGIN_USER, ERROR_FLAG)

    def logout_user(self, message_data, client: NetworkManager):
        msg = message_data.decode().split("|")
        if msg[0] == OK_FLAG.decode():
            client.user.is_online = False
            client.user.active_client = None
            client.user = None
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.LOGOUT_USER, OK_FLAG)
        else:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.LOGOUT_USER, ERROR_FLAG)

    def get_client_list(self, client: NetworkManager):
        if client.user.active_room:
            msg = "|".join([f"{user.user_id}|{user.username}"for user in client.user.active_room.get_user_list()])
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.GET_CLIENT_LIST, msg.encode())
        else:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.GET_CLIENT_LIST, ERROR_FLAG)

    def get_room_list(self, client: NetworkManager):
        # print([user.user_id for user in client.active_room.get_user_list()])
        # print([room.room_name for room in client.get_room_list()])
        msg = "|".join([room.room_name for room in client.user.get_room_list()])
        Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.GET_ROOM_LIST, msg.encode())

    def get_new_room_id(self):
        if len(self._rooms) == 0:
            return 0
        else:
            return self._rooms[-1].room_id + 1

    def create_room(self, message_data, client: NetworkManager):
        room = self.find_room_by_name(message_data.decode())
        if room:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.CREATE_ROOM, ERROR_FLAG)
            return
        room_id = self.get_new_room_id()
        room = Room(room_id=room_id, room_name=message_data.decode(), owner=client.user)
        self._rooms.append(room)
        client.user.active_room = room
        self.create_chat(room)
        print(f"[ROOM-CREATE] {SERVER} room - {room}\nroom list - {self._rooms}\nclient active room - {client.user.active_room}")
        # room.add_user_to_room(client)
        Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.CREATE_ROOM, OK_FLAG+b"|"+message_data)

    def delete_room(self, message_data, client: NetworkManager):
        if client.user.active_room.room_name == message_data.decode():
            room = self.find_room_by_id(client.user.active_room.room_id)
            if room and room.is_owner(client.user):
                room.delete_room_for_users()
                self._rooms.remove(room)
                self._chats.remove(room.chat)
                Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.DELETE_ROOM, OK_FLAG+b"|"+message_data)
            else:
                Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.DELETE_ROOM, ERROR_FLAG)
        else:
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.DELETE_ROOM, ERROR_FLAG)

    # def get_users_in_room(self, room):
    #     return room.get_user_list()

    def join_room(self, message_data, client: NetworkManager):
        room = self.find_room_by_name(message_data.decode())
        if room:
            room.add_user_to_room(client.user)
            client.user.active_room = room
            Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.JOIN_ROOM, OK_FLAG+b"|"+message_data)
            # ОБНОВЛЕНИЕ ДАННЫХ КОМНАТЫ ДЛЯ ПОЛЬЗОВАТЕЛЯ

            for user in room.get_user_list():
                self.get_client_list(user.active_client)
                if user.is_video_stream:
                    Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.VIDEO,
                                             START_FLAG+b"|"+str(user.user_id).encode())
                if user.is_voice_stream:
                    print(f"start audio for {client.user.username}")
                    Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.AUDIO,
                                             START_FLAG+b"|"+str(user.user_id).encode())
                if user.is_screen_stream:
                    Message.send_message_tcp(client.cmd_tcp_socket_client, MessageType.SCREENSHARE,
                                             START_FLAG+b"|"+str(user.user_id).encode())
            self.update_user_chat(client)
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

    def screenshare_handler(self, client: NetworkManager):
        for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
        # for user in client.user.active_room.get_user_list():
            if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:
                Message.send_message_tcp(cl.cmd_tcp_socket_client, MessageType.SCREENSHARE,
                                         START_FLAG+b"|"+str(client.user.user_id).encode())
        while client.user.is_screen_stream:
            data = Message.receive_large_message_udp(client.screen_udp_socket_server)
            # data = Message.recv_large_message_udp(client.screen_udp_socket_server)
            # for user in client.user.active_room.get_user_list():
            for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
                # print(f"Sended to - {user}")
                # print(f"data - {data}")
                if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:
                    threading.Thread(target=Message.send_large_message_udp, args=(cl.screen_udp_socket_server,
                                                                                  MessageType.SCREENSHARE, data[1],
                                                                                  cl.address,
                                                                                  cl.screen_udp_port_client,)).start()
        for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
            if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:
                Message.send_message_tcp(cl.cmd_tcp_socket_client, MessageType.SCREENSHARE,
                                         STOP_FLAG+b"|"+str(client.user.user_id).encode())

    def audio_handler(self, client: NetworkManager):
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

        for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
            if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:
                Message.send_message_tcp(cl.cmd_tcp_socket_client, MessageType.AUDIO,
                                         START_FLAG+b"|"+str(client.user.user_id).encode())
        while client.user.is_voice_stream:
            data = Message.receive_message_udp(client.voice_udp_socket_server)
            for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
                if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:

                    threading.Thread(target=Message.send_message_udp, args=(cl.voice_udp_socket_server,
                                                                            MessageType.AUDIO, data[1], cl.address,
                                                                            cl.voice_udp_port_client,)).start()
        for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
            if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:
                Message.send_message_tcp(cl.cmd_tcp_socket_client, MessageType.AUDIO,
                                         STOP_FLAG+b"|"+str(client.user.user_id).encode())

    def video_handler(self, client: NetworkManager):
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

        for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
            if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:
                Message.send_message_tcp(cl.cmd_tcp_socket_client, MessageType.VIDEO,
                                         START_FLAG+b"|"+str(client.user.user_id).encode())
        while client.user.is_video_stream:
            data = Message.receive_large_message_udp(client.video_udp_socket_server)
            for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
                if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:
                    threading.Thread(target=Message.send_large_message_udp, args=(cl.video_udp_socket_server,
                                                                                  MessageType.VIDEO, data[1],
                                                                                  cl.address,
                                                                                  cl.video_udp_port_client,)).start()
        for cl in [user.active_client for user in client.user.active_room.get_user_list()]:
            if client.user.user_id != cl.user.user_id and client.user.active_room == cl.user.active_room:
                Message.send_message_tcp(cl.cmd_tcp_socket_client, MessageType.VIDEO,
                                         STOP_FLAG+b"|"+str(client.user.user_id).encode())

    def broadcast_message(self):
        pass

    def get_all_rooms(self):
        pass
