import asyncio
from datetime import datetime, timedelta
from app.services.notification_service import get_notifications
from app.data.parser.parser import parse_schedule, get_today_timestamp
from app.config.config import get_lesson_times

async def notification_worker(bot):
    while True:
        now = datetime.now()

        notifications = get_notifications()

        for n in notifications:
            group = n["group"]
            lesson_num = n["lesson"]
            minutes_before = n["minutes_before"]

            schedule = parse_schedule(group, get_today_timestamp())
            today = str(now.date())
            lessons = schedule.get(today, [])

            for lesson in lessons:
                if lesson["number_lesson"] == lesson_num:
                    lesson_time_str = get_lesson_times[lesson_num]
                    lesson_time = datetime.strptime(lesson_time_str.split(" - ")[0], "%H:%M")

                    lesson_datetime = now.replace(
                        hour=lesson_time.hour,
                        minute=lesson_time.minute,
                        second=0,
                        microsecond=0
                    )

                    notify_time = lesson_datetime - timedelta(minutes=minutes_before)

                    # если сейчас время напоминания
                    if abs((now - notify_time).total_seconds()) < 30:
                        await bot.send_message(
                            n["user_id"],
                            f"🔔 Напоминание!\nСкоро {lesson_num} пара"
                        )

        await asyncio.sleep(30)