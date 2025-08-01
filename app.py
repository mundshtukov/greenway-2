import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from handlers import start, button, registration, faq, handle_message
from config import BOT_TOKEN, PORT
from flask import Flask
from threading import Thread
import signal
import sys

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Flask приложение для health check (требуется для Render)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!"

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

# Глобальная переменная для хранения экземпляра бота
updater = None

def setup_bot():
    """Настройка и запуск Telegram бота"""
    global updater
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return False
    
    try:
        # Создание и настройка Telegram бота
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher

        # Регистрация обработчиков команд
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("registration", registration))
        dp.add_handler(CommandHandler("faq", faq))

        # Регистрация обработчиков сообщений и callback
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        dp.add_handler(CallbackQueryHandler(button))

        # Обработка ошибок
        def error_handler(update, context):
            logger.error(f"Update {update} caused error {context.error}")

        dp.add_error_handler(error_handler)

        # Запуск бота в отдельном потоке
        def run_bot():
            try:
                logger.info("Запуск бота...")
                updater.start_polling(drop_pending_updates=True)
                logger.info("Бот запущен успешно!")
                updater.idle()
            except Exception as e:
                logger.error(f"Ошибка при работе бота: {e}")

        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при настройке бота: {e}")
        return False

# Инициализация бота при запуске модуля
if setup_bot():
    logger.info("Бот инициализирован успешно")
else:
    logger.error("Ошибка инициализации бота")

if __name__ == '__main__':
    # Если запускается напрямую, запускаем Flask сервер
    app.run(host='0.0.0.0', port=PORT, debug=False)
