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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

access_token = None
token_expiry = 0
token_lock = threading.Lock()

def get_access_token():
    global access_token, token_expiry
    
    with token_lock:
        # Проверяем, не обновил ли токен другой поток
        if access_token and time.time() < token_expiry:
            return access_token
            
        client_id = os.environ.get('GIGACHAT_CLIENT_ID')
        client_secret = os.environ.get('GIGACHAT_CLIENT_SECRET')

        if not client_id or not client_secret:
            logger.error("Ошибка: GIGACHAT_CLIENT_ID или GIGACHAT_CLIENT_SECRET не установлены")
            return None

        # Попробуем несколько вариантов API
        apis_to_try = [
            {
                'url': 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth',
                'scope': 'GIGACHAT_API_PERS'
            },
            {
                'url': 'https://gigachat.devices.sberbank.ru/api/v1/oauth',
                'scope': 'GIGACHAT_API_PERS'
            }
        ]

        auth_key = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

        for api_config in apis_to_try:
            try:
                logger.info(f"Попытка получения токена через: {api_config['url']}")
                
                payload = {'scope': api_config['scope']}
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                    'RqUID': str(uuid.uuid4()),
                    'Authorization': f'Basic {auth_key}'
                }

                response = requests.post(
                    api_config['url'], 
                    headers=headers, 
                    data=payload, 
                    verify=False, 
                    timeout=30
                )
                
                logger.info(f"Статус ответа: {response.status_code}")
                logger.info(f"Тело ответа: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'access_token' in data:
                        access_token = data['access_token']
                        
                        # Устанавливаем время истечения
                        if 'expires_in' in data:
                            token_expiry = time.time() + int(data['expires_in']) - 300
                        else:
                            # По умолчанию токен живет 30 минут
                            token_expiry = time.time() + 1800 - 300
                        
                        logger.info(f"Токен успешно получен! Истекает в: {time.ctime(token_expiry)}")
                        return access_token
                    else:
                        logger.error(f"Нет access_token в ответе: {data}")
                else:
                    logger.warning(f"Неуспешный ответ от {api_config['url']}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Ошибка при запросе к {api_config['url']}: {e}")
                continue

        logger.error("Не удалось получить токен ни через один API")
        return None

def get_gigachat_response(message: str, context: CallbackContext) -> str:
    global access_token
    
    # Простые fallback ответы если GigaChat недоступен
    fallback_responses = [
        "Привет! 👋 Я бот Greenway! Расскажи, что тебя интересует: продукты или бизнес-возможности? 😊",
        "Давай поговорим о Greenway! 🌱 Хочешь узнать о наших эко-продуктах или возможностях заработка? 💚",
        "Интересный вопрос! 🤔 Но лучше всего обратиться к наставнику https://t.me/mundshtukova - она все расскажет! 📞",
        "Ой! 😅 Давай лучше я покажу тебе наши продукты или расскажу о бизнесе с Greenway! 🚀"
    ]
    
    # Проверяем наличие токена
    if not access_token or time.time() > (token_expiry - 60):
        logger.info("Обновляем токен...")
        if not get_access_token():
            logger.warning("Не удалось получить токен, используем fallback")
            # Используем простой fallback
            import random
            return random.choice(fallback_responses)

    # Инициализация счетчика попыток
    if not context.user_data.get('gigachat_attempts'):
        context.user_data['gigachat_attempts'] = 0

    if context.user_data['gigachat_attempts'] >= 3:
        context.user_data['gigachat_attempts'] = 0
        if context.user_data.get('last_response_was_fallback'):
            return "Кажется, ты занят 😄 Напиши наставнику (https://t.me/mundshtukova), она поможет с Greenway!"
        context.user_data['last_response_was_fallback'] = True
        return "Ой, давай вернемся к Greenway! 😊 Хочешь узнать о продуктах или о бизнесе?"

    # Пробуем разные модели GigaChat
    models_to_try = ['GigaChat', 'GigaChat-Pro', 'GigaChat:latest']
    
    for model in models_to_try:
        try:
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            prompt = (
                f"Ты бот Greenway, отвечай живо, дружелюбно, только о продуктах Greenway "
                f"(более 1000 продуктов и 30+ брендов), бизнесе или регистрации. "
                f"Не обсуждай другие темы, используй эмодзи, перенаправляй к сценарию. "
                f"Ответ должен быть коротким. Пользователь написал: '{message}'"
            )

            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 100,
                'temperature': 0.7
            }

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'RqUID': str(uuid.uuid4())
            }

            logger.info(f"Запрос к GigaChat с моделью: {model}")
            response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                context.user_data['gigachat_attempts'] += 1
                context.user_data['last_response_was_fallback'] = False
                
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    logger.warning(f"Неожиданный формат ответа от модели {model}")
                    continue
            elif response.status_code == 401:
                logger.warning("Токен истек, пробуем обновить...")
                if get_access_token():
                    # Обновляем заголовок и пробуем еще раз
                    headers['Authorization'] = f'Bearer {access_token}'
                    response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            return result['choices'][0]['message']['content']
                break
            else:
                logger.warning(f"Ошибка {response.status_code} от модели {model}: {response.text}")
                continue
                
        except Exception as e:
            logger.error(f"Ошибка при запросе к модели {model}: {e}")
            continue

    # Если все попытки неудачны, используем fallback
    context.user_data['last_response_was_fallback'] = True
    import random
    return random.choice(fallback_responses)

def refresh_token_periodically():
    """Фоновое обновление токена"""
    while True:
        try:
            time.sleep(300)  # Проверяем каждые 5 минут
            if time.time() > (token_expiry - 300):  # За 5 минут до истечения
                logger.info("Время обновить токен...")
                get_access_token()
        except Exception as e:
            logger.error(f"Ошибка в фоновом обновлении токена: {e}")
            time.sleep(300)

def start_token_refresh():
    """Запуск сервиса токенов"""
    logger.info("Запуск сервиса обновления токенов...")
    
    # Не блокируем запуск приложения если токен не получен
    try:
        get_access_token()
    except Exception as e:
        logger.error(f"Ошибка при получении первичного токена: {e}")
        logger.info("Продолжаем запуск без токена, будем использовать fallback ответы")
    
    # Запускаем фоновое обновление
    thread = threading.Thread(target=refresh_token_periodically, daemon=True)
    thread.start()
    logger.info("Фоновое обновление токенов запущено")

# Инициализация при импорте модуля
start_token_refresh()
