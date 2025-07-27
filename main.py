import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from handlers import start, button, registration, faq, handle_message
from config import BOT_TOKEN, PORT
from flask import Flask
from threading import Thread

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

def run_flask():
    """Запускает Flask сервер в отдельном потоке"""
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

def main():
    """Основная функция для запуска бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    try:
        # Запуск Flask сервера в отдельном потоке
        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        logger.info("Flask сервер запущен")
        
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

        # Запуск бота
        logger.info("Запуск бота...")
        updater.start_polling(drop_pending_updates=True)
        logger.info("Бот запущен успешно!")
        updater.idle()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    main()
