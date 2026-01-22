from telegram import Bot
from telegram.error import TelegramError
from utils.logger import get_logger

logger = get_logger(__name__)

class Notifier:
    def __init__(self, token, chat_id):
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        logger.info(f"Notifier initialized for chat_id: {chat_id}")

    def send(self, message):
        """Send message to Telegram with error handling"""
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Message sent successfully: {message[:50]}...")
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            raise

