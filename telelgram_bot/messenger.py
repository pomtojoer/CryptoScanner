# Telegram modules
import telegram

def send_message(token, chat_id, message):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.HTML)
