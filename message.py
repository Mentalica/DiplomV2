import struct
import socket
from messageType import MessageType
from consts import *


class Message:
    @staticmethod
    def receive_message_tcp(sock: socket.socket):
        # Проверяем наличие данных в сокете
        if not sock.recv(1, socket.MSG_PEEK):
            return None, None  # Возвращаем None, если нет данных в сокете
        # Получаем длину сообщения
        message_length_bytes = sock.recv(4)
        # message_length = struct.unpack('!I', message_length_bytes)[0]
        message_length = int.from_bytes(message_length_bytes, byteorder='big')

        # Получаем тип сообщения
        message_type_bytes = sock.recv(4)
        # message_type = struct.unpack('!I', message_type_bytes)[0]
        message_type = int.from_bytes(message_type_bytes, byteorder='big')

        # Получаем данные сообщения
        message_data = b''
        while len(message_data) < message_length:
            chunk = sock.recv(message_length - len(message_data))
            if not chunk:
                raise RuntimeError("Socket connection broken")
            message_data += chunk
        # print(f"[tuple] {MESSAGE}: msg type: {message_type}\n\tmsg data: {message_data}")
        # Возвращаем распакованное сообщение
        return message_type, message_data

    @staticmethod
    def receive_message_udp(sock: socket.socket):
        message, address = sock.recvfrom(MAX_BYTES_UDP)
        message_type = int.from_bytes(message[:4], byteorder='big')
        # print(f"RECV {MESSAGE}: {message_type}")
        message_data = message[4:]
        return message_type, message_data, address

    @staticmethod
    def send_message_tcp(sock: socket.socket, message_type, message_data):
        # Упаковка длины сообщения и его типа
        message_type = message_type
        message_length = len(message_data)
        header = struct.pack('!II', message_length, message_type)

        # Отправка заголовка и данных
        sock.sendall(header + message_data)

    @staticmethod
    def send_message_udp(sock: socket.socket, message_type, message_data: bytes, dest_addr: str,
                         dest_port: int):
        # Упаковываем сообщение в нужном формате
        # print(f"SEND {MESSAGE}: {message_type}")
        packed_message = struct.pack(f"!I {len(message_data)}s", message_type, message_data)

        # Отправляем упакованное сообщение на указанный адрес и порт
        sock.sendto(packed_message, (dest_addr, dest_port))

    @staticmethod
    def send_large_message_udp(sock: socket.socket, message_type, message_data: bytes, dest_addr: str,
                               dest_port: int, chunk_size=MAX_BYTES_UDP):
        # Упаковываем сообщение в нужном формате
        # print(f"SEND {MESSAGE}: {message_type}")
        packed_message = struct.pack(f"!I {len(message_data)}s", message_type, message_data)

        # Определяем размер сообщения и количество необходимых частей
        message_length = len(packed_message)
        num_chunks = (message_length // chunk_size) + 1

        # Разбиваем сообщение на части
        chunks = [packed_message[i:i + chunk_size] for i in range(0, message_length, chunk_size)]

        # Отправляем каждую часть сообщения на указанный адрес и порт
        for i, chunk in enumerate(chunks):
            # Определяем флаги начала и конца сообщения
            start_flag = i == 0
            end_flag = i == num_chunks - 1

            # Упаковываем часть сообщения в нужном формате
            chunk_header = struct.pack("!??I", start_flag, end_flag, i)

            # Отправляем часть сообщения на указанный адрес и порт
            sock.sendto(chunk_header + chunk, (dest_addr, dest_port))

    # @staticmethod
    # def receive_big_message_udp(sock: socket.socket):
    #     message_chunks = []
    #     message_size_bytes = sock.recv(4)  # первые 4 байта - размер сообщения
    #     message_size = int.from_bytes(message_size_bytes, byteorder='big')
    #     bytes_received = 0
    #
    #     while bytes_received < message_size:
    #         chunk, address = sock.recvfrom(MAX_BYTES_UDP)
    #         message_chunks.append(chunk)
    #         bytes_received += len(chunk)
    #
    #     # склеиваем все чанки и возвращаем сообщение
    #     message = b''.join(message_chunks)
    #     message_type = int.from_bytes(message[:4], byteorder='big')
    #     message_data = message[4:]
    #     return message_type, message_data, address

    @staticmethod
    def receive_big_message_udp(sock: socket.socket):
        # Принимаем размер сообщения
        message_size_bytes, address = sock.recvfrom(4)
        message_size = int.from_bytes(message_size_bytes, byteorder='big')

        # Принимаем данные сообщения
        received_data = b""
        while len(received_data) < message_size:
            data, address = sock.recvfrom(MAX_BYTES_UDP)
            received_data += data

        return received_data

    @staticmethod
    def send_big_message_udp(sock: socket.socket, message: bytes, dest_addr: str, dest_port: int):
        # Отправляем размер сообщения
        message_size_bytes = len(message).to_bytes(4, byteorder='big')
        sock.sendto(message_size_bytes, (dest_addr, dest_port))

        # Отправляем данные сообщения порциями
        total_sent = 0
        while total_sent < len(message):
            sent = sock.sendto(message[total_sent:], (dest_addr, dest_port))
            total_sent += sent
