import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers import start, button, registration, faq, handle_message
from config import BOT_TOKEN, PORT
from flask import Flask, request
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
    app.run(host='0.0.0.0', port=PORT, debug=False)

async def main():
    """Основная функция для запуска бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Запуск Flask сервера в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Создание и настройка Telegram бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("registration", registration))
    application.add_handler(CommandHandler("faq", faq))

    # Регистрация обработчиков сообщений и callback
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    logger.info("Запуск бота...")
    await application.run_polling()
    logger.info("Бот запущен успешно!")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
