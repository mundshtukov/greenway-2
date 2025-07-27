import os
import requests
import base64
import uuid
import time
import threading
import urllib3
import logging
from telegram.ext import CallbackContext

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Подавление предупреждения

access_token = None
token_expiry = 0

def get_access_token():
    global access_token, token_expiry
    client_id = os.environ.get('GIGACHAT_CLIENT_ID')
    client_secret = os.environ.get('GIGACHAT_CLIENT_SECRET')

    if not client_id or not client_secret:
        logger.error("Ошибка: GIGACHAT_CLIENT_ID или GIGACHAT_CLIENT_SECRET не установлены")
        return None

    auth_key = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {auth_key}'
    }

    try:
        logger.info(f"Отправка запроса на токен: url={url}")
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
        access_token = data['access_token']
        token_expiry = time.time() + data['expires_at'] / 1000 - 300
        logger.info(f"Токен получен успешно")
        return access_token
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning(f"Ошибка 429: Превышен лимит запросов. Ждем 120 секунд.")
            time.sleep(120)
            return get_access_token()
        logger.error(f"Ошибка получения токена: {e}")
        return None
    except requests.exceptions.Timeout:
        logger.error("Таймаут при получении токена")
        return None
    except Exception as e:
        logger.error(f"Ошибка получения токена: {e}")
        return None

def check_models():
    global access_token
    if not access_token:
        access_token = get_access_token()
    if not access_token:
        logger.error("Ошибка: Токен не получен для проверки моделей.")
        return None
    url = "https://gigachat.devices.sberbank.ru/api/v1/models"
    headers = {'Accept': 'application/json', 'Authorization': f'Bearer {access_token}'}
    try:
        logger.info(f"Проверка доступных моделей")
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        logger.info(f"Доступные модели получены")
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка проверки моделей: {e}")
        return None

def refresh_token_periodically():
    """Периодическое обновление токена"""
    while True:
        try:
            get_access_token()
            sleep_time = max(0, token_expiry - time.time() - 60)
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                time.sleep(3600)  # Если что-то пошло не так, ждем час
        except Exception as e:
            logger.error(f"Ошибка в refresh_token_periodically: {e}")
            time.sleep(3600)  # В случае ошибки ждем час

def get_gigachat_response(message: str, context: CallbackContext) -> str:
    global access_token
    
    # Проверяем токен
    if not access_token or time.time() > token_expiry:
        access_token = get_access_token()

    if not access_token:
        return "Ой, давай вернемся к Greenway! 😊 Хочешь узнать о продуктах или о бизнесе?"

    # Инициализация счетчика попыток
    if not context.user_data.get('gigachat_attempts'):
        context.user_data['gigachat_attempts'] = 0

    # Проверка лимита попыток
    if context.user_data['gigachat_attempts'] >= 2:
        context.user_data['gigachat_attempts'] = 0
        if context.user_data.get('last_response_was_fallback'):
            return "Кажется, ты занят 😄 Напиши наставнику (@mundshtukova), она поможет с Greenway!"
        context.user_data['last_response_was_fallback'] = True
        return "Ой, давай вернемся к Greenway! 😊 Хочешь узнать о продуктах или о бизнесе?"

    models_to_try = ['GigaChat-Pro', 'GigaChat-2']
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    prompt = (
        f"Ты бот Greenway, отвечай живо, дружелюбно, только о продуктах Greenway (более 1000 продуктов и 30+ брендов), бизнесе или регистрации. "
        f"Не обсуждай другие темы, используй эмодзи, перенаправляй к сценарию. Ответ должен быть коротким. "
        f"Пользователь написал: '{message}'"
    )

    for model in models_to_try:
        payload = {
            'model': model, 
            'messages': [{'role': 'user', 'content': prompt}], 
            'max_tokens': 100
        }
        headers = {
            'Content-Type': 'application/json', 
            'Accept': 'application/json', 
            'Authorization': f'Bearer {access_token}'
        }
        try:
            logger.info(f"Отправка запроса GigaChat: model={model}")
            response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
            response.raise_for_status()
            result = response.json()
            context.user_data['gigachat_attempts'] += 1
            context.user_data['last_response_was_fallback'] = False
            return result['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.warning(f"Ошибка 403 для модели {model}: Доступ запрещен. Пробуем следующую.")
                models = check_models()
                if models:
                    logger.info(f"Доступные модели: {models}")
            else:
                logger.error(f"Ошибка GigaChat для модели {model}: {e}")
            continue
        except requests.exceptions.Timeout:
            logger.error(f"Таймаут для модели {model}")
            continue
        except Exception as e:
            logger.error(f"Ошибка GigaChat для модели {model}: {e}")
            continue

    context.user_data['gigachat_attempts'] = 0
    context.user_data['last_response_was_fallback'] = True
    return "Ой, давай вернемся к Greenway! 😊 Хочешь узнать о продуктах или о бизнесе?"

# Запуск периодического обновления токена
def start_token_refresh():
    """Запуск обновления токена в отдельном потоке"""
    refresh_thread = threading.Thread(target=refresh_token_periodically, daemon=True)
    refresh_thread.start()

# Инициализация при импорте модуля
start_token_refresh()
check_models()
