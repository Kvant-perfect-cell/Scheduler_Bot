
from datetime import datetime, timedelta

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MONTHS = [
    "января", "февраля", "марта", "апреля",
    "мая", "июня", "июля", "августа",
    "сентября", "октября", "ноября", "декабря"
]

def format_date(date_str: str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = datetime.now().date()

    weekday = WEEKDAYS[date_obj.weekday()]
    day = date_obj.day
    month = MONTHS[date_obj.month - 1]

    if date_obj == today:
        return f"Сегодня ({weekday}, {day} {month})"
    elif date_obj == today + timedelta(days=1):
        return f"Завтра ({weekday}, {day} {month})"

    return f"{weekday}, {day} {month}"