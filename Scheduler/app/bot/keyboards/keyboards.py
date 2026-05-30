from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.data.parser.parser import get_groups_by_courses
from app.utils.date_utils import format_date
from datetime import datetime
from app.config.config import get_lesson_times

LESSON_TIMES = get_lesson_times()

def chunked(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def main_keyboard(group=None):
    if group:
        text = f"Моя группа ({group})"
    else:
        text = "Моя группа (сохранить)"

    buttons = [
        [InlineKeyboardButton(text="Расписание на сегодня", callback_data=f"my_today")],
        [InlineKeyboardButton(text="🔔 Напоминания", callback_data="notifications")],
        [InlineKeyboardButton(text=text, callback_data="my_group")],
        [InlineKeyboardButton(text="Выбрать группу", callback_data=f"courses")],
        
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def my_group_actions_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="my_today")],
        [InlineKeyboardButton(text="Завтра", callback_data="my_tomorrow")],
        [InlineKeyboardButton(text="Подробно", callback_data="my_full")],
        [InlineKeyboardButton(text="Сменить группу", callback_data="change_group")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def courses_inline_keyboard():
    courses, newest_course = get_groups_by_courses()

    # course_hundred = newest_course - (int(course) - 1) * 100

    buttons = []
    for course in range(1, 5):
        buttons.append([InlineKeyboardButton(text=str(f"{course} курс"), callback_data=f"course:{course}")])

    # кнопка назад
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Доступные группы

def groups_inline_keyboard(course):
    courses, newest_course = get_groups_by_courses()
    course_hundred = newest_course - (int(course) - 1) * 100

    rows = []
    for row in chunked(courses.get(course_hundred, []), 6):  # по 6 в ряд
        rows.append([
            InlineKeyboardButton(text=str(group), callback_data=f"group:{group}")
            for group in row
        ])

    # кнопка назад
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_courses")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)

def days_keyboard(days):
    buttons = []

    for date in sorted(days):
        date_obj = datetime.strptime(date, "%Y-%m-%d")

        if date_obj.weekday() == 6: #skip sunday
            continue

        buttons.append([
            InlineKeyboardButton(
                text=format_date(date),
                callback_data=f"day:{date}"
            )
        ])
        
    # кнопка назад
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Пары для напоминаний
def lessons_keyboard():
    buttons = []

    for i in range(1, 7):
        buttons.append([
            InlineKeyboardButton(
                text=f"Пара {i} ({LESSON_TIMES[i]})",
                callback_data=f"notify_lesson:{i}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Просмотр напоминаний
def notifications_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Добавить напоминание",
            callback_data="notifications_add"
        )],
        [InlineKeyboardButton(
            text="Мои напоминания",
            callback_data="notifications_list"
        )],
        [InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back_to_main"
        )]
    ])

def notification_list_keyboard(all_notifications, user_id):
    rows = []

    for idx, n in enumerate(all_notifications):
        if n["user_id"] != user_id:
            continue

        rows.append([
            InlineKeyboardButton(
                text=f"❌ Пара {n['lesson']} ({n['minutes_before']} мин)",
                callback_data=f"delete_notify:{idx}"
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="notifications"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)

# Кнопки Назад

def back_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Выбрать курс", callback_data="back_to_courses")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_to_days_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_days")]
    ])
