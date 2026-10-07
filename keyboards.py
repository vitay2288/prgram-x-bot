from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выбери действие ⚡"
    )
    kb.row(KeyboardButton("👤 Профиль"), KeyboardButton("💰 Заработать"))
    kb.row(KeyboardButton("🎁 Бонус"), KeyboardButton("🧾 Чек"))
    kb.row(KeyboardButton("👥 Рефералы"), KeyboardButton("🏆 Уровни"))
    kb.row(KeyboardButton("📕 Правила"), KeyboardButton("📖 Инструкция"))
    return kb
