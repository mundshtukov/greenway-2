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

def run_flask():
    """Запускает Flask сервер в отдельном потоке"""
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Ошибка при запуске Flask сервера: {e}")

def signal_handler(sig, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info('Получен сигнал завершения. Останавливаем бота...')
    sys.exit(0)

def main():
    """Основная функция для запуска бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return 1
    
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Запуск Flask сервера в отдельном потоке
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info(f"Flask сервер запущен на порту {PORT}")
        
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

        # Запуск бота
        logger.info("Запуск бота...")
        updater.start_polling(drop_pending_updates=True)
        logger.info("Бот запущен успешно!")
        updater.idle()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)