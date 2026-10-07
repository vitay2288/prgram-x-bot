from database import get_pending_checks, reject_task, confirm_task

async def check_subscriptions(bot):
    pending = get_pending_checks()
    for item in pending:
        ut_id, user_id, task_id, reward, channel_link = item
        try:
            chat_id = channel_link.replace("https://t.me/", "@")
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status in ["left", "kicked"]:
                reject_task(ut_id, reward)
                await bot.send_message(
                    user_id,
                    f"⚠️ Ты отписался от канала. Списано {reward} искр."
                )
            else:
                confirm_task(ut_id)
        except Exception:
            pass
