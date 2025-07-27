from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from keyboards import get_main_keyboard, get_role_inline_keyboard, get_product_inline_keyboard, get_business_inline_keyboard, get_order_inline_keyboard, get_faq_inline_keyboard
from gigachat import get_gigachat_response

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_message = (
        f"Привет, {user.first_name}! 😊 Добро пожаловать в Greenway — эко-маркетплейс с более чем 1000 продуктов и 30+ брендов! "
        f"У нас есть всё для дома, здоровья, красоты и даже питомцев. Тысячи людей находят здесь любимые продукты и даже своё дело! 💚 Выбери пункт меню ниже 👇 или задай свой вопрос."
    )
    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())
    await update.message.reply_text("", reply_markup=get_role_inline_keyboard())  # Пустое сообщение для отображения только кнопок

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = query.data

    if text == "role_client":
        await query.edit_message_text(
            "Классный выбор! 😄 Greenway — это эко-маркетплейс с более чем 1000 продуктов и 30+ брендов! "
            "От салфеток без химии до косметики, питания и товаров для питомцев — каждый найдёт своё. "
            "Тысячи людей уже выбрали Greenway для экожизни! 💚",
            reply_markup=get_product_inline_keyboard()
        )
    elif text == "role_partner":
        await query.edit_message_text(
            "Супер, ты интересуешься бизнесом с Greenway! 🚀 Это шанс создать свою команду, делиться классными экопродуктами и получать бонусы за рекомендации. "
            "Многие находят в Greenway любимое дело и экологичный образ жизни! 💚",
            reply_markup=get_business_inline_keyboard()
        )
    elif text == "product_cleaning":
        await query.edit_message_text(
            "Салфетки Greenway — это магия чистоты! 🧼 Убирают всё без химии, идеальны для дома, машины, да хоть для чего! "
            "Люди обожают их за простоту и экологичность. Хочешь заказать или посмотреть отзывы в клиентском чате? 💬",
            reply_markup=get_order_inline_keyboard()
        )
    elif text == "product_teas":
        await query.edit_message_text(
            "Наши чаи — это вкус и забота о здоровье! 🍵 С травами, ягодами, для энергии и иммунитета. "
            "Тысячи людей начинают день с Greenway! Хочешь попробовать или заглянуть в клиентский чат? 💬",
            reply_markup=get_order_inline_keyboard()
        )
    elif text == "product_health":
        await query.edit_message_text(
            "Продукты для здоровья — это про твоё самочувствие! 💪 Коктейли, витамины, добавки — всё экологичное. "
            "Многие находят здесь поддержку для активной жизни! Закажем или посмотрим отзывы в чате? 💬",
            reply_markup=get_order_inline_keyboard()
        )
    elif text == "product_cosmetics":
        await query.edit_message_text(
            "Косметика Greenway — это натуральная красота! 💄 Уход за лицом, телом, волосами — всё экологичное и эффективное. "
            "Тысячи людей перешли на неё! Хочешь попробовать или узнать, что говорят в чате? 💬",
            reply_markup=get_order_inline_keyboard()
        )
    elif text == "product_home":
        await query.edit_message_text(
            "Товары для дома — это комфорт и экология! 🏠 Моющие средства, аксессуары для кухни — всё безопасное. "
            "Хозяйки в восторге! Закажем или заглянем в клиентский чат? 💬",
            reply_markup=get_order_inline_keyboard()
        )
    elif text == "back_product":
        await query.edit_message_text(
            "Выбери категорию продуктов:",
            reply_markup=get_product_inline_keyboard()
        )
    elif text == "business_start":
        await query.edit_message_text(
            "Начать проще простого! 😊 Регистрируешься через наставника, пробуешь продукты и делишься ими с друзьями — как рекомендовать любимый фильм, только с бонусами! "
            "Тысячи людей так начали своё дело с Greenway. Хочу соединить тебя с наставником (@mundshtukova), она всё расскажет.",
            reply_markup=get_business_inline_keyboard()
        )
    elif text == "business_mentor":
        await query.edit_message_text(
            "Круто! 😄 Напиши наставнику (@mundshtukova), она поможет с регистрацией и поделится всеми секретами. "
            "Многие начинали так же и теперь обожают Greenway! Хочешь посмотреть продукты для старта?",
            reply_markup=get_role_inline_keyboard()
        )
    elif text == "order_store":
        await query.edit_message_text(
            "Отлично! 😊 Перейди в интернет-магазин, там огромный выбор: https://greenwayglobal.com/invite/client/bnASdxUgzX "
            "Люди находят здесь всё для экожизни! Если нужна помощь, напиши мне или наставнику (@mundshtukova). Что дальше?",
            reply_markup=get_main_keyboard()
        )
    elif text == "order_chat":
        await query.edit_message_text(
            "Круто, в клиентском чате делятся отзывами, обзорами и проводят розыгрыши! 😄 Напиши наставнику (@mundshtukova), она даст ссылку. "
            "Хочешь ещё посмотреть продукты?",
            reply_markup=get_role_inline_keyboard()
        )
    elif text == "faq_registration":
        await query.edit_message_text(
            "Регистрация — это легко! 😄 Хочешь стать клиентом — переходи в интернет-магазин: https://greenwayglobal.com/invite/client/bnASdxUgzX "
            "Для партнерства напиши наставнику (@mundshtukova), она всё объяснит. Тысячи людей так начали своё дело! Хочешь подробности?",
            reply_markup=get_faq_inline_keyboard()
        )
    elif text == "faq_products":
        await query.edit_message_text(
            "В Greenway более 1000 продуктов, и каждый находит любимое! 💚 Салфетки без химии, чаи для здоровья, косметика, товары для дома — всё экологичное. "
            "Тысячи людей выбирают их каждый день! Хочешь заглянуть в клиентский чат за отзывами или заказать? 🛍️",
            reply_markup=get_order_inline_keyboard()
        )
    elif text == "faq_difference":
        await query.edit_message_text(
            "Greenway — это эко-маркетплейс с 1000+ продуктов и 30+ брендов! 😊 Мы заботимся о природе и здоровье, предлагаем экологичные товары и возможность создать своё дело. "
            "Люди ценят нас за качество и масштаб! Хочешь узнать о продуктах или бизнесе?",
            reply_markup=get_role_inline_keyboard()
        )
    elif text == "faq_why":
        await query.edit_message_text(
            "Greenway — это про экологию и возможности! 🌿 Свыше 1000 продуктов для всей семьи, от уборки до красоты, плюс шанс построить своё дело. "
            "Тысячи людей по всему миру выбирают Greenway за качество и заботу о планете! Хочешь попробовать продукты или узнать про бизнес?",
            reply_markup=get_role_inline_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Продукты 🌱":
        await update.message.reply_text(
            "Классный выбор! 😄 Greenway — это эко-маркетплейс с более чем 1000 продуктов и 30+ брендов! "
            "От салфеток без химии до косметики, питания и товаров для питомцев — каждый найдёт своё. "
            "Тысячи людей уже выбрали Greenway для экожизни! 💚",
            reply_markup=get_product_inline_keyboard()
        )
    elif text == "Бизнес 🚀":
        await update.message.reply_text(
            "Супер, ты интересуешься бизнесом с Greenway! 🚀 Это шанс создать свою команду, делиться классными экопродуктами и получать бонусы за рекомендации. "
            "Многие находят в Greenway любимое дело и экологичный образ жизни! 💚",
            reply_markup=get_business_inline_keyboard()
        )
    elif text == "Связаться с наставником 📞":
        await update.message.reply_text(
            "Супер, свяжись с наставником (@mundshtukova)! 😊 Она поможет с регистрацией или даст ссылку на клиентский чат, где куча полезного: отзывы, акции, истории успеха. "
            "Тысячи людей начинали с такого шага! Хочешь продолжить с заказом?",
            reply_markup=get_main_keyboard()
        )
    elif text == "Интернет-магазин 🛒":
        await update.message.reply_text(
            "Класс, давай выберем что-то крутое! 🛒 Greenway — это эко-маркетплейс с более чем 1000 продуктов и 30+ брендов! "
            "От уборки до косметики — всё для экожизни. Тысячи людей обожают наши продукты! Хочешь заказать или заглянуть в клиентский чат за отзывами и акциями?",
            reply_markup=get_order_inline_keyboard()
        )
    elif text == "Клиентский чат 💬":
        await update.message.reply_text(
            "Круто, в клиентском чате делятся отзывами, обзорами и проводят розыгрыши! 😄 Напиши наставнику (@mundshtukova), она даст ссылку. "
            "Хочешь ещё посмотреть продукты?",
            reply_markup=get_role_inline_keyboard()
        )
    elif text == "Частые вопросы ❓":
        await update.message.reply_text(
            "Хочешь узнать больше? 😊 Вот ответы на популярные вопросы:",
            reply_markup=get_faq_inline_keyboard()
        )
    else:
        response = await get_gigachat_response(text, context)
        await update.message.reply_text(response, reply_markup=get_main_keyboard())

async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Готов начать? 🚀 Напиши @mundshtukova для регистрации!",
        reply_markup=get_main_keyboard()
    )

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хочешь узнать больше? 😊 Вот ответы на популярные вопросы:",
        reply_markup=get_faq_inline_keyboard()
    )
