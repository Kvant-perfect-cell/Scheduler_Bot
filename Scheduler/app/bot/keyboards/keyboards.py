from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.data.parser.parser import get_groups_by_courses

def chunked(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Расписание на сегодня", callback_data=f"today")],
        [InlineKeyboardButton(text="Выбрать группу", callback_data=f"courses")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

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



# def courses_keyboard():
#     newKeyboard = [
#         [KeyboardButton(text="Назад")],
#     ]

#     for i in range(1, 5):
#         newKeyboard.append([KeyboardButton(text = f"{i} курс")])

#     return ReplyKeyboardMarkup(
#         keyboard=newKeyboard,
#         resize_keyboard=True
#     )

# def groups_keyboard(course):
#     newKeyboard = [
#         [KeyboardButton(text="Назад")],
#     ]

#     courses, newest_course = get_groups_by_courses()
#     course_hundred = newest_course - (int(course) - 1) * 100

#     for group in courses.get(course_hundred, []):
#         newKeyboard.append([KeyboardButton(text=str(group))])

#     return ReplyKeyboardMarkup(
#         keyboard=newKeyboard,
#         resize_keyboard=True
#     )
