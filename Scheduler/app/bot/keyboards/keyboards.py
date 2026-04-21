from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.data.parser.parser import get_available_groups

# def main_keyboard():
#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="📅 Сегодня")],
#             [KeyboardButton(text="📆 Выбрать дату")],
#         ],
#         resize_keyboard=True
#     )

#groups_keyboard
def main_keyboard():
    for i, k in get_available_groups().items():
        print(i, k)
    return ReplyKeyboardMarkup(
        keyboard=[
        ],
    )