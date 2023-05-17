import telebot

class TelegramAPI:
    def __init__(self):
        self.chat_id = None
        self.token = None
        self.telegram_bot = None

    def connect_telegram_bot(self, chat_id, token):
        """
        Подключает Telegram-бота с указанным токеном и сохраняет его экземпляр в атрибут telegram_bot.
        """
        self.token = token
        self.chat_id = chat_id
        self.telegram_bot = telebot.TeleBot(token)

    def send_message_to_telegram(self, message):
        """
        Отправляет сообщение в Telegram-чат, связанный с данным чатом в приложении.
        """
        if self.telegram_bot:
            print(f"{self.chat_id}\n {message}")
            self.telegram_bot.send_message(chat_id=self.chat_id, text=message)