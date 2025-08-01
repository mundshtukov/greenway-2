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
    
    with token_lock:  # Защита от одновременного обновления токена
        # Проверяем, не обновил ли токен другой поток
        if access_token and time.time() < token_expiry:
            return access_token
            
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
            logger.info("Запрос на получение токена")
            response = requests.post(url, headers=headers, data=payload, verify=False, timeout=30)
            response.raise_for_status()
            data = response.json()
            access_token = data['access_token']
            # Исправляем расчет времени истечения
            token_expiry = time.time() + data['expires_in'] - 300  # expires_in в секундах
            logger.info(f"Токен успешно получен. Истекает в: {time.ctime(token_expiry)}")
            return access_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка получения токена: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Статус код: {e.response.status_code}")
                logger.error(f"Тело ответа: {e.response.text}")
            return None

def refresh_token_periodically():
    while True:
        try:
            get_access_token()
            # Обновляем токен за 5 минут до истечения
            sleep_time = max(300, token_expiry - time.time() - 300)
            logger.info(f"Следующее обновление токена через {sleep_time} секунд")
            time.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Ошибка при обновлении токена: {e}")
            time.sleep(300)  # Повторяем через 5 минут при ошибке

def get_gigachat_response(message: str, context: CallbackContext) -> str:
    global access_token
    logger.info(f"Текущее время: {time.ctime(time.time())}")
    logger.info(f"Время истечения токена: {time.ctime(token_expiry)}")
    logger.info(f"Токен доступен: {'Да' if access_token else 'Нет'}")

    # Проверка и обновление токена с запасом времени
    if not access_token or time.time() > (token_expiry - 60):
        logger.info("Обновляем токен...")
        if not get_access_token():
            return "Ошибка авторизации. Попробуй позже 🛠️"

    if not context.user_data.get('gigachat_attempts'):
        context.user_data['gigachat_attempts'] = 0

    if context.user_data['gigachat_attempts'] >= 2:
        context.user_data['gigachat_attempts'] = 0
        if context.user_data.get('last_response_was_fallback'):
            return "Кажется, ты занят 😄 Напиши наставнику (@mundshtukova), она поможет с Greenway!"
        context.user_data['last_response_was_fallback'] = True
        return "Ой, давай вернемся к Greenway! 😊 Хочешь узнать о продуктах или о бизнесе?"

    model = 'GigaChat'
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    prompt = (
        f"Ты бот Greenway, отвечай живо, дружелюбно, только о продуктах Greenway (более 1000 продуктов и 30+ брендов), "
        f"бизнесе или регистрации. Не обсуждай другие темы, используй эмодзи, перенаправляй к сценарию. "
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

    try:
        logger.info(f"Запрос к GigaChat: модель={model}")
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        
        # Детальное логирование ответа
        logger.info(f"Статус код ответа: {response.status_code}")
        
        if response.status_code == 401:
            logger.warning("Получен 401 Unauthorized, обновляем токен...")
            if get_access_token():
                headers['Authorization'] = f'Bearer {access_token}'
                response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
            else:
                return "Ошибка авторизации. Попробуй позже 🛠️"
        
        response.raise_for_status()
        result = response.json()
        context.user_data['gigachat_attempts'] += 1
        context.user_data['last_response_was_fallback'] = False
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"Неожиданный формат ответа: {result}")
            return "Получен некорректный ответ от сервера 🤔"
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при обращении к GigaChat: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Статус код: {e.response.status_code}")
            logger.error(f"Тело ответа: {e.response.text}")
        context.user_data['last_response_was_fallback'] = True
        return "Ой, техническая неполадка 😓 Попробуй ещё раз или напиши наставнику!"

def start_token_refresh():
    # Получаем первый токен при запуске
    get_access_token()
    # Запускаем фоновое обновление
    threading.Thread(target=refresh_token_periodically, daemon=True).start()

# Инициализация при импорте модуля
start_token_refresh()