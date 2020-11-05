import telebot


class TelegramAPI:

    def __init__(self, bot_token, bot_chat_id):
        self.bot_token = bot_token
        self.bot_chatID = bot_chat_id
        self.tb = telebot.TeleBot(self.bot_token)

    def send_text(self, bot_message):
        self.tb.send_message(self.bot_chatID, bot_message)

    def send_image(self, route):
        photo = open(route, 'rb')
        self.tb.send_photo(self.bot_chatID, photo)
