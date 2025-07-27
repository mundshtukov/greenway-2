from telegram import Update
from telegram.ext import CallbackContext
from keyboards import get_main_keyboard, get_role_inline_keyboard, get_product_inline_keyboard, get_business_inline_keyboard, get_order_inline_keyboard, get_faq_inline_keyboard
from gigachat import get_gigachat_response
import logging

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    welcome_message = (
        f"Привет, {user.first_name}! 😊 Добро пожаловать в Greenway — эко-маркетплейс с более чем 1000 продуктов и 30+ брендов! "
        f"У нас есть всё для дома, здоровья, красоты и даже питомцев. Тысячи людей находят здесь любимые продукты и даже своё дело! 💚 Выбери пункт меню ниже 👇 или задай свой вопрос."
    )
    update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())
    update.message.reply_text("", reply_markup=get_role_inline_keyboard())  # Пустое сообщение для отображения только кнопок

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    text = query.data
    
    logger.info(f"Получен callback: {text}")

    try:
        if text == "role_client":
            query.edit_message_text(
                "Классный выбор! 😄 Greenway — это эко-маркетплейс с более чем 1000 продуктов и 30+ брендов! "
                "От салфеток без химии до косметики, питания и товаров для питомцев — каждый найдёт своё. "
                "Тысячи людей уже выбрали Greenway для экожизни! 💚",
                reply_markup=get_product_inline_keyboard()
            )
        elif text == "role_partner":
            query.edit_message_text(
                "Супер, ты интересуешься бизнесом с Greenway! 🚀 Это шанс создать свою команду, делиться классными экопродуктами и получать бонусы за рекомендации. "
                "Многие находят в Greenway любимое дело и экологичный образ жизни! 💚",
                reply_markup=get_business_inline_keyboard()
            )
        elif text == "product_cleaning":
            query.edit_message_text(
                "Салфетки Greenway — это магия чистоты! 🧼 Убирают всё без химии, идеальны для дома, машины, да хоть для чего! "
                "Люди обожают их за простоту и экологичность. Хочешь заказать или посмотреть отзывы в клиентском чате? 💬",
                reply_markup=get_order_inline_keyboard()
            )
        elif text == "product_teas":
            query.edit_message_text(
                "Наши чаи — это вкус и забота о здоровье! 🍵 С травами, ягодами, для энергии и иммунитета. "
                "Тысячи людей начинают день с Greenway! Хочешь попробовать или заглянуть в клиентский чат? 💬",
                reply_markup=get_order_inline_keyboard()
            )
        elif text == "product_health":
            query.edit_message_text(
                "Продукты для здоровья — это про твоё самочувствие! 💪 Коктейли, витамины, добавки — всё экологичное. "
                "Многие находят здесь поддержку для активной жизни! Закажем или посмотрим отзывы в чате? 💬",
                reply_markup=get_order_inline_keyboard()
            )
        elif text == "product_cosmetics":
            query.edit_message_text(
                "Косметика Greenway — это натуральная красота! 💄 Уход за лицом, телом, волосами — всё экологичное и эффективное. "
                "Тысячи людей перешли на неё! Хочешь попробовать или узнать, что говорят в чате? 💬",
                reply_markup=get_order_inline_keyboard()
            )
        elif text == "product_home":
            query.edit_message_text(
                "Товары для дома — это комфорт и экология! 🏠 Моющие средства, аксессуары для кухни — всё безопасное. "
                "Хозяйки в восторге! Закажем или заглянем в клиентский чат? 💬",
                reply_markup=get_order_inline_keyboard()
            )
        elif text == "back_product":
            query.edit_message_text(
                "Выбери категорию продуктов:",
                reply_markup=get_product_inline_keyboard()
            )
        elif text == "business_start":
            query.edit_message_text(
                "Начать проще простого! 😊 Регистрируешься через наставника, пробуешь продукты и делишься ими с друзьями — как рекомендовать любимый фильм, только с бонусами! "
                "Тысячи людей так начали своё дело с Greenway. Хочу соединить тебя с наставником (@mundshtukova), она всё расскажет.",
                reply_markup=get_business_inline_keyboard()
            )
        elif text == "business_mentor":
            query.edit_message_text(
                "Круто! 😄 Напиши наставнику (@mundshtukova), она поможет с регистрацией и поделится всеми секретами. "
                "Многие начинали так же и теперь обожают Greenway! Хочешь посмотреть продукты для старта?",
                reply_markup=get_role_inline_keyboard()
            )
        elif text == "order_store":
            # ИСПРАВЛЕНИЕ: Убрал reply_markup и сократил сообщение
            query.edit_message_text(
                "Отлично! 😊 Переходи в интернет-магазин:\n"
                "https://greenwayglobal.com/invite/client/bnASdxUgzX\n\n"
                "Люди находят здесь всё для экожизни! Если нужна помощь, напиши наставнику (@mundshtukova)."
            )
            # Отправляем новое сообщение с клавиатурой
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Что дальше?",
                reply_markup=get_role_inline_keyboard()
            )
        elif text == "order_chat":
            query.edit_message_text(
                "Круто, в клиентском чате делятся отзывами, обзорами и проводят розыгрыши! 😄 Напиши наставнику (@mundshtukova), она даст ссылку. "
                "Хочешь ещё посмотреть продукты?",
                reply_markup=get_role_inline_keyboard()
            )
        elif text == "faq_registration":
            query.edit_message_text(
                "Регистрация — это легко! 😄 Хочешь стать клиентом — переходи в интернет-магазин: https://greenwayglobal.com/invite/client/bnASdxUgzX "
                "Для партнерства напиши наставнику (@mundshtukova), она всё объяснит. Тысячи людей так начали своё дело! Хочешь подробности?",
                reply_markup=get_faq_inline_keyboard()
            )
        elif text == "faq_products":
            query.edit_message_text(
                "В Greenway более 1000 продуктов, и каждый находит любимое! 💚 Салфетки без химии, чаи для здоровья, косметика, товары для дома — всё экологичное. "
                "Тысячи людей выбирают их каждый день! Хочешь заглянуть в клиентский чат за отзывами или заказать? 🛍️",
                reply_markup=get_order_inline_keyboard()
            )
        elif text == "faq_difference":
            query.edit_message_text(
                "Greenway — это эко-маркетплейс с 1000+ продуктов и 30+ брендов! 😊 Мы заботимся о природе и здоровье, предлагаем экологичные товары и возможность создать своё дело. "
                "Люди ценят нас за качество и масштаб! Хочешь узнать о продуктах или бизнесе?",
                reply_markup=get_role_inline_keyboard()
            )
        elif text == "faq_why":
            query.edit_message_text(
                "Greenway — это про экологию и возможности! 🌿 Свыше 1000 продуктов для всей семьи, от уборки до красоты, плюс шанс построить своё дело. "
                "Тысячи людей по всему миру выбирают Greenway за качество и заботу о планете! Хочешь попробовать продукты или узнать про бизнес?",
                reply_markup=get_role_inline_keyboard()
            )
        else:
            logger.warning(f"Неизвестный callback: {text}")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике кнопки {text}: {e}")
        # Отправляем fallback сообщение
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Что-то пошло не так 😅 Попробуй еще раз или напиши наставнику (@mundshtukova)",
            reply_markup=get_main_keyboard()
        )

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "Продукты 🌱":
        update.message.reply_text(
            "Классный выбор! 😄 Greenway — это эко-маркетплейс с более чем 1000 продуктов и 30+ брендов! "
            "От салфеток без химии до косметики, питания и товаров для питомцев — каждый найдёт своё. "
            "Тысячи людей уже выбрали Greenway для экожизни! 💚",
            reply_markup=get_product_inline_keyboard()
        )
    elif text == "Бизнес 🚀":
        update.message.reply_text(
            "Супер, ты интересуешься бизнесом с Greenway! 🚀 Это шанс создать свою команду, делиться классными экопродуктами и получать бонусы за рекомендации. "
            "Многие находят в Greenway любимое дело и экологичный образ жизни! 💚",
            reply_markup=get_business_inline_keyboard()
        )
    elif text == "Связаться с наставником 📞":
        update.message.reply_text(
            "Супер, свяжись с наставником (@mundshtukova)! 😊 Она поможет с регистрацией или даст ссылку на клиентский чат, где куча полезного: отзывы, акции, истории успеха. "
            "Тысячи людей начинали с такого шага! Хочешь продолжить с заказом?",
            reply_markup=get_main_keyboard()
        )
    elif text == "Интернет-магазин 🛒":
        update.message.reply_text(
            "Класс, давай выберем что-то крутое! 🛒 Greenway — это эко-маркетплейс с более чем 1000 продуктов и 30+ брендов! "
            "От уборки до косметики — всё для экожизни. Тысячи людей обожают наши продукты! Хочешь заказать или заглянуть в клиентский чат за отзывами и акциями?",
            reply_markup=get_order_inline_keyboard()
        )
    elif text == "Клиентский чат 💬":
        update.message.reply_text(
            "Круто, в клиентском чате делятся отзывами, обзорами и проводят розыгрыши! 😄 Напиши наставнику (@mundshtukova), она даст ссылку. "
            "Хочешь ещё посмотреть продукты?",
            reply_markup=get_role_inline_keyboard()
        )
    elif text == "Частые вопросы ❓":
        update.message.reply_text(
            "Хочешь узнать больше? 😊 Вот ответы на популярные вопросы:",
            reply_markup=get_faq_inline_keyboard()
        )
    else:
        response = get_gigachat_response(text, context)
        update.message.reply_text(response, reply_markup=get_main_keyboard())

def registration(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Готов начать? 🚀 Напиши @mundshtukova для регистрации!",
        reply_markup=get_main_keyboard()
    )

def faq(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Хочешь узнать больше? 😊 Вот ответы на популярные вопросы:",
        reply_markup=get_faq_inline_keyboard()
    )
