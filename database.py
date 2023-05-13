from typing import List

import mysql.connector

from chat import Chat
from chatMessage import ChatMessage
from room import Room
from user import User


class Database:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.connection = mysql.connector.connect(
            host=self.host, user=self.username, password=self.password, database=self.database
        )
        # self.cursor = self.connection.cursor()

    def create_users_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL
            )
        """)
        cursor.close()

    def create_chat_messages_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                chat_id INT,
                chat_message_id INT,
                message_time VARCHAR(255) NOT NULL,
                message VARCHAR(255) NOT NULL,
                user_id INT 
            )
        """)
        cursor.close()

    def create_rooms_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INT,
                room_name VARCHAR(255) NOT NULL,
                owner_id INT,
                chat_id INT
            )
        """)
        cursor.close()

    def create_chats_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INT,
                room_id INT
            )
        """)
        cursor.close()

    def create_room_user_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_user (
                room_id INT,
                user_id INT
            )
        """)
        cursor.close()

    def insert_room_user(self, room_id, user_id):
        cursor = self.connection.cursor()
        query = "INSERT IGNORE INTO room_user (room_id, user_id) VALUES (%s, %s)"
        values = (room_id, user_id)
        cursor.execute(query, values)
        self.connection.commit()
        print(f"Room - {room_id}, User {user_id} inserted into database with ID: {cursor.lastrowid}")
        cursor.close()

    def create_tables(self):
        self.create_chats_table()
        self.create_rooms_table()
        self.create_chat_messages_table()
        self.create_users_table()
        self.create_room_user_table()

    def insert_user(self, user: User):
        cursor = self.connection.cursor()
        query = "INSERT INTO users (user_id, username, password, email) VALUES (%s, %s, %s, %s)"
        values = (user.user_id, user.username, user.password, user.email)
        cursor.execute(query, values)
        self.connection.commit()
        print(f"User {user.username} inserted into database with ID: {cursor.lastrowid}")
        cursor.close()

    def get_all_users(self):
        cursor = self.connection.cursor()
        query = "SELECT user_id, username, password, email FROM users"
        cursor.execute(query)
        result = cursor.fetchall()
        users = []
        for row in result:
            user_id, username, password, email = row
            user = User(user_id=user_id, username=username, password=password, email=email)
            users.append(user)
        cursor.close()
        return users

    def insert_room(self, room: Room):
        cursor = self.connection.cursor()
        query = "INSERT INTO rooms (room_id, room_name, owner_id, chat_id) VALUES (%s, %s, %s, %s)"
        values = (room.room_id, room.room_name, room.owner.user_id, room.chat.chat_id)
        cursor.execute(query, values)
        self.connection.commit()
        print(f"Room {room.room_name} inserted into database with ID: {cursor.lastrowid}")
        cursor.close()

    def insert_chat_message(self, chat_msg: ChatMessage):
        cursor = self.connection.cursor()
        query = "INSERT INTO chat_messages (chat_id, chat_message_id, message_time, message, user_id) " \
                "VALUES (%s, %s, %s, %s, %s)"
        values = (chat_msg.chat_id, chat_msg.chat_message_id, chat_msg.message_time,
                  chat_msg.message, chat_msg.user.user_id)
        cursor.execute(query, values)
        self.connection.commit()
        print(f"Chat_message {chat_msg.chat_id} inserted into database with ID: {cursor.lastrowid}")
        cursor.close()

    def insert_chat(self, chat: Chat):
        cursor = self.connection.cursor()
        query = "INSERT INTO chats (chat_id, room_id) VALUES (%s, %s)"
        values = (chat.chat_id, chat.room.room_id)
        cursor.execute(query, values)
        self.connection.commit()
        print(f"Chat {chat.chat_id} inserted into database with ID: {cursor.lastrowid}")
        cursor.close()

    def get_all_rooms(self):
        cursor = self.connection.cursor()
        cursor_chat = self.connection.cursor()
        query = "SELECT room_id, room_name, owner, chat_id FROM rooms"
        query_chat = "SELECT room_id, room_name, owner, chat_id FROM rooms"
        cursor.execute(query)
        result = cursor.fetchall()
        rooms = []
        for row in result:
            room_id, room_name, owner, chat_id = row
            room = Room(room_id=room_id, room_name=room_name, owner=owner, chat=email)
            rooms.append(room)
        cursor.close()
        return rooms

    def get_all_data(self):
        # Get all users
        users_cursor = self.connection.cursor()
        query = "SELECT user_id, username, password, email FROM users"
        users_cursor.execute(query)
        result = users_cursor.fetchall()
        users = []
        for row in result:
            user_id, username, password, email = row
            user = User(user_id=user_id, username=username, password=password, email=email)
            users.append(user)
        users_cursor.close()

        # Get all chat_messages
        chat_msgs_cursor = self.connection.cursor()
        chat_msgs_query = "SELECT chat_id, chat_message_id, message_time, message, user_id FROM chat_messages"
        chat_msgs_cursor.execute(chat_msgs_query)
        result = chat_msgs_cursor.fetchall()
        chat_msgs = []
        for row in result:
            chat_id, chat_message_id, message_time, message, user_id = row
            chat_msg = ChatMessage(chat_id=chat_id, chat_message_id=chat_message_id, message_time=message_time,
                                   message=message, user=self.find_user_by_id(users, user_id))
            chat_msgs.append(chat_msg)
        chat_msgs_cursor.close()

        # Get all rooms and chats
        rooms_cursor = self.connection.cursor()
        query = "SELECT room_id, room_name, owner_id, chat_id FROM rooms"
        rooms_cursor.execute(query)
        result = rooms_cursor.fetchall()
        rooms = []
        chats = []
        for row in result:
            room_id, room_name, owner_id, chat_id = row
            room = Room(room_id=room_id, room_name=room_name, owner=self.find_user_by_id(users, owner_id))

            room_user_query = "SELECT room_id, user_id FROM room_user WHERE room_id = %s"
            room_user_cursor = self.connection.cursor()
            room_user_cursor.execute(room_user_query, (room_id,))
            room_user_result = room_user_cursor.fetchall()
            for room_user in room_user_result:
                room_id, user_id = room_user
                print(user_id)
                room.add_user_to_room(self.find_user_by_id(users, user_id))
                room.add_room_to_user(self.find_user_by_id(users, user_id))

            chat_query = "SELECT chat_id, room_id FROM chats WHERE chat_id = %s"
            chat_cursor = self.connection.cursor()
            chat_cursor.execute(chat_query, (chat_id,))
            chat_result = chat_cursor.fetchone()
            chat_id, chat_name = chat_result
            messages = self.get_chat_messages_for_chat(chat_id, chat_msgs)
            chat = Chat(chat_id=chat_id, room=room, chat_messages=messages)  # Здесь нужно получать данные чата
            room.chat = chat
            rooms.append(room)
            chats.append(chat)
        rooms_cursor.close()

        return users, rooms, chats

    def get_chat_messages_for_chat(self, chat_id, chat_msgs: List[ChatMessage]):
        msgs = []
        for chat_msg in chat_msgs:
            if chat_msg.chat_id == chat_id:
                msgs.append(chat_msg)
        return msgs

    def find_user_by_id(self, users: [User], user_id):
        for user in users:
            if user.user_id == user_id:
                return user
        return None

    def find_chat_by_id(self, chats: [Chat], chat_id):
        for chat in chats:
            if chat.chat_id == chat_id:
                return chat
        return None

    def find_room_by_id(self, rooms: [Room], room_id):
        for room in rooms:
            if room.room_id == room_id:
                return room
        return None
