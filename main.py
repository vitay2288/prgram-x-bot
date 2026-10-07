import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import start, tasks, checks_img
from handlers.checks import check_subscriptions

async def daily_check(bot):
    while True:
        await asyncio.sleep(86400)
        try:
            await check_subscriptions(bot)
        except Exception as e:
            print(f"Ошибка проверки: {e}")

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(checks_img.router)
    asyncio.create_task(daily_check(bot))
    print("PR GRAM X запущен ⚡")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
