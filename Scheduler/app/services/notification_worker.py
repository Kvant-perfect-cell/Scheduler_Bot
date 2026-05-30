import asyncio
from datetime import datetime, timedelta

from app.services.notification_service import get_notifications
from app.config.config import get_lesson_times

LESSON_TIMES = get_lesson_times()

async def notification_worker(bot):
    while True:
        now = datetime.now()

        notifications = get_notifications()

        for n in notifications:
            if n.get("sent", False):
                continue

            lesson_num = n["lesson"]
            minutes_before = n["minutes_before"]

            lesson_time_str = LESSON_TIMES[lesson_num]

            lesson_time = datetime.strptime(
                lesson_time_str.split(" - ")[0],
                "%H:%M"
            )

            lesson_datetime = now.replace(
                hour=lesson_time.hour,
                minute=lesson_time.minute,
                second=0,
                microsecond=0
            )

            notify_time = lesson_datetime - timedelta(
                minutes=minutes_before
            )

            diff = (now - notify_time).total_seconds()

            if 0 <= diff <= 60:

                await bot.send_message(
                    n["user_id"],
                    f"🔔 Напоминание!\n"
                    f"Через {minutes_before} мин. начнётся {lesson_num} пара."
                )

                n["sent"] = True

        notifications[:] = [
            n for n in notifications
            if not n.get("sent", False)
        ]

        await asyncio.sleep(15)