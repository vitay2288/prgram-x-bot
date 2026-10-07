from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from database import get_user, add_balance
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

router = Router()

def create_check_image(user_id, username, amount):
    img = Image.new("RGB", (600, 300), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_tiny = ImageFont.load_default()

    draw.rectangle([10, 10, 590, 290], outline=(255, 215, 0), width=3)
    draw.text((300, 60), "ИСКРЫ", fill=(255, 215, 0), font=font_big, anchor="mm")
    draw.text((300, 150), f"{amount}", fill=(255, 255, 255), font=font_big, anchor="mm")
    draw.text((300, 230), f"ID: {user_id}", fill=(150, 150, 150), font=font_small, anchor="mm")
    draw.text((300, 260), f"@{username} • {datetime.now().strftime('%d.%m.%Y')}",
              fill=(150, 150, 150), font=font_tiny, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

@router.message(F.text.startswith("/check"))
async def send_check(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: `/check <сумма>`", parse_mode="Markdown")
        return

    try:
        amount = int(args[1])
    except ValueError:
        await message.answer("❌ Сумма должна быть числом.")
        return

    user = get_user(message.from_user.id)
    if not user or user[2] < amount:
        balance = user[2] if user else 0
        await message.answer(f"❌ Недостаточно искр. Твой баланс: **{balance}**", parse_mode="Markdown")
        return

    add_balance(message.from_user.id, -amount)

    buf = create_check_image(message.from_user.id, message.from_user.username or "user", amount)
    photo = BufferedInputFile(buf.read(), filename="check.png")

    await message.answer_photo(
        photo,
        caption=f"⚡ **Чек на {amount} искр**\n\nПерешли его другу или используй в розыгрыше!",
        parse_mode="Markdown"
    )
