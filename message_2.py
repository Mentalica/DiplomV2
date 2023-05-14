import struct
import socket
from messageType import MessageType
from consts import *

received_msgs = {}


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

    @staticmethod
    def send_large_message_udp_by_id(sock: socket.socket, message_data: bytes, dest_addr: str,
                                     dest_port: int, id, chunk_size=MAX_BYTES_UDP - 100):

        packed_message = struct.pack(f"!{len(message_data)}s", message_data)
        message_length = len(message_data)
        num_chunks = (message_length // chunk_size)
        chunks = [packed_message[i:i + chunk_size] for i in range(0, message_length, chunk_size)]

        for i, chunk in enumerate(chunks):
            # start_flag = i == 0
            # end_flag = i == num_chunks - 1
            chunk_header = struct.pack("!III", num_chunks, i, id)
            sock.sendto(chunk_header + chunk, (dest_addr, dest_port))

    @staticmethod
    def receive_large_message_udp_by_id(sock: socket.socket, id, chunk_size=MAX_BYTES_UDP):
        address_id = None
        if id in received_msgs:  # Если уже были получены chunks
            # print(f"ID: {id}. received chunks - {received_msgs[id][0]}, requirements chunks size - {received_msgs[id][1]}")
            if received_msgs[id][0] == received_msgs[id][1]:  # Если chunks уже все готовы, то отправляем данные
                sorted_chunks = [received_msgs[id][2][i] for i in sorted(received_msgs[id][2])]
                address = received_msgs[id][3]
                del received_msgs[id]
                message_data = b"".join(sorted_chunks)
                return message_data, address
            else:  # Если есть данные, но не все
                chunk_header, address = sock.recvfrom(chunk_size)
                num_chunks, chunk_index, recv_id = struct.unpack("!III", chunk_header[:12])
                if recv_id == id:  # В прочитанном сообщении нужные нам данные
                    received_msgs[id][2][chunk_index] = chunk_header[12:]
                    for i in range(received_msgs[id][0], num_chunks):  # Дочитываем все chunks
                        chunk_header, address = sock.recvfrom(chunk_size)
                        num_chunks_tmp, chunk_index, recv_id_tmp = struct.unpack("!III", chunk_header[:12])
                        if recv_id_tmp == id: # При считывании новых данных, данные соответствуют требуемым нам
                            # Тогда добавляем chunk и увеличваем индекс полученных чанков
                            received_msgs[id][2][chunk_index] = chunk_header[12:]
                            received_msgs[id][0] = i
                        else:
                            # Если новые данные не соответствуют нашим ожидаемым, то сохраняем их в словаре,
                            # чтобы считать потом
                            if recv_id_tmp in received_msgs:  # создаем ключ в словаре если он не создан. Заполняем
                                # словарь
                                received_msgs[recv_id_tmp][0] += 1
                                received_msgs[recv_id_tmp][2][chunk_index] = chunk_header[12:]
                            else:
                                received_msgs[recv_id_tmp] = [0, num_chunks_tmp, {chunk_index: chunk_header[12:]},
                                                              address]
                            i -= 1 # Чтобы считать еще 1 пакет, так как данные были не наши

                # Данные были дополнены, теперь возвращаем
                sorted_chunks = [received_msgs[id][2][i] for i in sorted(received_msgs[id][2])]
                address = received_msgs[id][3]
                del received_msgs[id]
                message_data = b"".join(sorted_chunks)
                return message_data, address
        else: # Данных вообще не было, получаем все, попутно не свои добавляя в словарь
            chunk_header, address = sock.recvfrom(chunk_size)
            num_chunks, chunk_index, recv_id = struct.unpack("!III", chunk_header[:12])
            # print(f"num_chunks: {num_chunks}. chunk_index - {chunk_index}, recv_id - {recv_id}")
            message_data = {}
            if recv_id == id:  # В прочитанном сообщении нужные нам данные
                message_data[chunk_index] = chunk_header[12:]

                for i in range(0, num_chunks):  # Дочитываем все chunks
                    chunk_header, address = sock.recvfrom(chunk_size)
                    num_chunks_tmp, chunk_index, recv_id_tmp = struct.unpack("!III", chunk_header[:12])
                    if recv_id_tmp == id:  # При считывании новых данных, данные соответствуют требуемым нам
                        # Тогда добавляем chunk и увеличваем индекс полученных чанков
                        address_id = address
                        message_data[chunk_index] = chunk_header[12:]
                    else:
                        # Если новые данные не соответствуют нашим ожидаемым, то сохраняем их в словаре,
                        # чтобы считать потом
                        if recv_id_tmp in received_msgs:  # Создаем ключ в словаре если он не создан. Заполняем
                            # словарь
                            received_msgs[recv_id_tmp][0] += 1
                            received_msgs[recv_id_tmp][2][chunk_index] = chunk_header[12:]
                        else:
                            received_msgs[recv_id_tmp] = [0, num_chunks_tmp, {chunk_index: chunk_header[12:]},
                                                          address]
                        i -= 1  # Чтобы считать еще 1 пакет, так как данные были не наши

            # Данные были дополнены, теперь возвращаем
            sorted_chunks = [message_data[i] for i in sorted(message_data)]
            message_data = b"".join(sorted_chunks)
            return message_data, address_id