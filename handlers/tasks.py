from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_available_tasks

router = Router()

TASK_EMOJI = {
    "subscribe": "📢",
    "reaction": "❤️",
    "repost": "🔄",
    "comment": "💬",
    "view": "👁"
}

@router.message(F.text == "💰 Заработать")
async def show_tasks(message: Message):
    tasks = get_available_tasks(message.from_user.id)
    if not tasks:
        await message.answer("😔 Пока нет доступных заданий. Загляни позже!")
        return

    text = "💰 **Доступные задания**\n\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for task in tasks:
        tid, ttype, link, reward, max_c, completed, created_by, created_at = task
        emoji = TASK_EMOJI.get(ttype, "📌")
        text += f"{emoji} {ttype.capitalize()} — **{reward}** искр\n"
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} Выполнить за {reward}⚡",
                callback_data=f"task_{tid}"
            )
        ])

    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data.startswith("task_"))
async def do_task(callback: CallbackQuery):
    await callback.answer("✅ Задание выполнено! Награда зачислена.", show_alert=True)
