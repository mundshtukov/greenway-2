import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from handlers import start, button, registration, faq, handle_message
from config import BOT_TOKEN, PORT
from flask import Flask
from threading import Thread
import sys

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Flask приложение для проверки здоровья (требуется для Render)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Бот работает!"

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

# Глобальная переменная для бота
updater = None

def setup_bot():
    """Настройка и запуск Telegram бота"""
    global updater
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return False
    
    try:
        # Создание и настройка бота
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher

        # Добавляем обработчики команд
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("registration", registration))
        dp.add_handler(CommandHandler("faq", faq))

        # Добавляем обработчики сообщений
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        dp.add_handler(CallbackQueryHandler(button))

        # Обработчик ошибок
        def error_handler(update, context):
            logger.error(f"Обновление {update} вызвало ошибку {context.error}")

        dp.add_error_handler(error_handler)

        # Запуск бота в отдельном потоке
        def run_bot():
            try:
                logger.info("Запускаем Telegram бота...")
                updater.start_polling(drop_pending_updates=True)
                logger.info("Бот успешно запущен!")
                updater.idle()
            except Exception as e:
                logger.error(f"Ошибка при работе бота: {e}")

        # Запускаем бота в фоновом режиме
        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        logger.info("Бот инициализирован и запущен в фоновом режиме")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при настройке бота: {e}")
        return False

# Инициализируем бота при загрузке модуля
logger.info("Инициализация бота...")
if setup_bot():
    logger.info("Бот успешно инициализирован")
else:
    logger.error("Ошибка инициализации бота")

# Если запускается напрямую
if __name__ == '__main__':
    logger.info(f"Запуск Flask сервера на порту {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
