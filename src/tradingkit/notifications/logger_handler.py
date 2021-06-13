from logging import Handler, Formatter, info
import datetime
from tradingkit.notifications.telegram_api import TelegramAPI


class RequestsHandler(Handler):

    def __init__(self, bot_token, bot_chat_id):
        self.bot = TelegramAPI(bot_token, bot_chat_id)
        super().__init__()

    def emit(self, record):
        if record.levelname == 'WARNING':
            log_entry = self.format(record)
            try:
                self.bot.send_text(log_entry)
            except Exception as e:
                info("Notification error:\n %s" % str(e))

class LogstashFormatter(Formatter):
    def __init__(self):
        super(LogstashFormatter, self).__init__()

    def format(self, record):
        t = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        return "INFO: {message}".format(message=record.msg, datetime=t)
