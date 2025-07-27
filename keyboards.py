from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Продукты 🌱"), KeyboardButton("Бизнес 🚀")],
        [KeyboardButton("Связаться с наставником 📞"), KeyboardButton("Интернет-магазин 🛒")],
        [KeyboardButton("Клиентский чат 💬"), KeyboardButton("Частые вопросы ❓")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_role_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("Узнать о продуктах 🌿", callback_data="role_client"),
         InlineKeyboardButton("Стать партнером 🤝", callback_data="role_partner")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_product_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("Салфетки 🧼", callback_data="product_cleaning"),
         InlineKeyboardButton("Чаи 🍵", callback_data="product_teas")],
        [InlineKeyboardButton("Здоровье 💪", callback_data="product_health"),
         InlineKeyboardButton("Косметика 💄", callback_data="product_cosmetics")],
        [InlineKeyboardButton("Товары для дома 🏠", callback_data="product_home"),
         InlineKeyboardButton("Назад ⬅️", callback_data="back_product")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_business_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("Как начать 🌟", callback_data="business_start"),
         InlineKeyboardButton("Связаться с наставником 📲", callback_data="business_mentor")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_order_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("Оформить заказ 🛍️", callback_data="order_store"),
         InlineKeyboardButton("Клиентский чат 💬", callback_data="order_chat")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_faq_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("Как работает регистрация? 📝", callback_data="faq_registration"),
         InlineKeyboardButton("Популярные продукты 🌺", callback_data="faq_products")],
        [InlineKeyboardButton("Чем отличается Greenway? 🌍", callback_data="faq_difference"),
         InlineKeyboardButton("Почему выбрать Greenway? 💚", callback_data="faq_why")]
    ]
    return InlineKeyboardMarkup(keyboard)