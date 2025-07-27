import os  # Импорт для работы с переменными окружения

# Переменные окружения, должны быть заданы в Render Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # Токен Telegram-бота
PORT = int(os.environ.get('PORT', 8000))  # Порт для веб-сервера (Render требует веб-сервер)