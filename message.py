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
    def send_large_message_udp(sock: socket.socket, message_type: int, message_data: bytes, dest_addr: str,
                               dest_port: int, chunk_size=MAX_BYTES_UDP - 100):

        packed_message = struct.pack(f"!I {len(message_data)}s", message_type, message_data)
        message_length = len(message_data)
        num_chunks = (message_length // chunk_size) + 1
        chunks = [packed_message[i:i + chunk_size] for i in range(0, message_length, chunk_size)]

        for i, chunk in enumerate(chunks):
            start_flag = i == 0
            end_flag = i == num_chunks - 1
            chunk_header = struct.pack("!??I", start_flag, end_flag, i)
            sock.sendto(chunk_header + chunk, (dest_addr, dest_port))

    @staticmethod
    def receive_large_message_udp(sock: socket.socket, chunk_size=MAX_BYTES_UDP):
        chunk_header, address = sock.recvfrom(chunk_size)

        message_chunks = {}
        start_flag, end_flag, chunk_index, message_type = struct.unpack(f"!??II", chunk_header[:10])
        message_chunks[0] = chunk_header[10:]

        start_of_message = start_flag
        end_of_message = end_flag

        while not end_of_message:
            # flag = True
            chunk_header, address = sock.recvfrom(chunk_size)
            start_flag, end_flag, chunk_index = struct.unpack("!??I", chunk_header[:6])
            start_of_message |= start_flag
            end_of_message |= end_flag
            message_chunks[chunk_index + 1] = chunk_header[6:]

        sorted_chunks = [message_chunks[i] for i in sorted(message_chunks)]
        message_data = b"".join(sorted_chunks)

        return message_type, message_data, address
