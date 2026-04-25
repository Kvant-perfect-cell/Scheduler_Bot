from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.data.parser.parser import get_groups_by_courses


def main_keyboard():
    newKeyboard = [
        [KeyboardButton(text="Расписание на сегодня")],
        [KeyboardButton(text="Выбрать группу")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=newKeyboard,
        resize_keyboard=True
    )


def courses_keyboard():
    newKeyboard = [
        [KeyboardButton(text="Назад")],
    ]

    for i in range(1, 5):
        newKeyboard.append([KeyboardButton(text = f"{i} курс")])

    return ReplyKeyboardMarkup(
        keyboard=newKeyboard,
        resize_keyboard=True
    )

def groups_keyboard(course):
    newKeyboard = [
        [KeyboardButton(text="Назад")],
    ]

    courses, newest_course = get_groups_by_courses()
    course_hundred = newest_course - (int(course) - 1) * 100

    for group in courses.get(course_hundred, []):
        newKeyboard.append([KeyboardButton(text=str(group))])

    return ReplyKeyboardMarkup(
        keyboard=newKeyboard,
        resize_keyboard=True
    )
