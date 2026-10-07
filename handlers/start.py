from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from database import (
    get_user, create_user, add_balance,
    can_take_bonus, set_bonus_date
)
from config import DAILY_BONUS, LEVELS
from keyboards import main_menu
from texts import WELCOME, RULES, INSTRUCTION

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref"):
        try:
            referrer_id = int(args[1][3:])
        except ValueError:
            pass

    user = get_user(message.from_user.id)
    if not user:
        create_user(message.from_user.id, message.from_user.username, referrer_id)

    await message.answer(WELCOME, reply_markup=main_menu(), parse_mode="Markdown")

@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала напиши /start")
        return
    text = f"""⚡ **Твой профиль PR GRAM X**

🆔 ID: `{user[0]}`
📅 Дата регистрации: {user[5]}
💰 Баланс: **{user[2]} искр**
🏆 Уровень: **{user[3]}**
👥 Реферал: {user[4] if user[4] else "нет"}
"""
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "🎁 Бонус")
async def bonus(message: Message):
    if can_take_bonus(message.from_user.id):
        user = get_user(message.from_user.id)
        level = user[3] if user else "Bronze"
        bonus_amount = DAILY_BONUS + LEVELS.get(level, {}).get("bonus", 0)
        add_balance(message.from_user.id, bonus_amount)
        set_bonus_date(message.from_user.id)
        await message.answer(
            f"🎁 Ты получил **{bonus_amount} искр**!\n"
            f"(Базовый: {DAILY_BONUS} + бонус уровня {level}: {LEVELS[level]['bonus']})\n\n"
            f"Приходи завтра!",
            parse_mode="Markdown"
        )
    else:
        await message.answer("⏳ Ты уже брал бонус сегодня. Возвращайся завтра!")

@router.message(F.text == "📕 Правила")
async def rules(message: Message):
    await message.answer(RULES, parse_mode="Markdown")

@router.message(F.text == "📖 Инструкция")
async def instruction(message: Message):
    await message.answer(INSTRUCTION, parse_mode="Markdown")

@router.message(F.text == "🏆 Уровни")
async def levels(message: Message):
    user = get_user(message.from_user.id)
    current = user[3] if user else "Bronze"
    text = "🏆 **Уровни PR GRAM X**\n\n"
    for name, data in LEVELS.items():
        mark = "✅" if name == current else "▫️"
        text += f"{mark} **{name}** — от {data['threshold']} искр (бонус +{data['bonus']})\n"
    text += f"\nТвой уровень: **{current}**"
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "👥 Рефералы")
async def refs(message: Message):
    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=ref{message.from_user.id}"
    await message.answer(
        f"👥 **Твоя реферальная ссылка:**\n`{link}`\n\n"
        f"За каждого друга — **9%** от его заработка навсегда.",
        parse_mode="Markdown"
    )

@router.message(F.text == "🧾 Чек")
async def check_button(message: Message):
    await message.answer(
        "🧾 **Создание чека**\n\n"
        "Напиши: `/check <сумма>`\n"
        "Например: `/check 1000`\n\n"
        "Бот сгенерирует картинку с надписью «Искры» и числом. "
        "Её можно переслать другу или использовать в розыгрыше.",
        parse_mode="Markdown"
    )
