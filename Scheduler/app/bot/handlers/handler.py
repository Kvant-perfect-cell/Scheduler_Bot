from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.bot.keyboards import keyboards
from app.services.schedule_service import get_schedule_for_today
from app.services.user_service import set_user_group, get_user_group
from app.data.parser.parser import get_base_info

router = Router()

user_groups = {}

LESSON_TIMES = {
    1: "08:30 - 9:50",
    2: "10:00 - 11:20",
    3: "11:30 - 12:50",
    4: "13:40 - 15:00",
    5: "15:10 - 16:30",
    6: "16:35 - 17:55",
}

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@router.message(
    Command("start")
)
@router.message(
    lambda message: message.text == "Назад"
)
async def start_handler(message: Message):
    get_base_info()
    await message.answer(
        "Привет! Выбери действие 👇",
        reply_markup=keyboards.main_keyboard()
    )


@router.message(
    lambda message: message.text == "Расписание на сегодня"
)
async def today_button_handler(message: Message):
    group = get_user_group(message.from_user.id)

    if not group:
        await message.answer("Сначала установи группу: /setgroup 501")
        return

    schedule = get_schedule_for_today(group)

    if not schedule:
        await message.answer("🎉 Сегодня пар нет!")
        return

    text = f"📅 Сегодня ({group}):\n\n"

    for lesson in schedule:
        time = LESSON_TIMES.get(lesson["time"], str(lesson["time"]))
        subject = lesson["subject"]
        teacher = lesson["teacher"]

        text += f"{time}\n{subject}\n👨‍🏫 {teacher}\n\n"

    for part in split_message(text):
        await message.answer(part)

@router.message(
    lambda message: message.text == "Выбрать группу"
)
async def select_group(message: Message):
   
    await message.answer(
        "Выберите курс:",
        reply_markup=keyboards.courses_keyboard()
    )

@router.message(
    lambda message: message.text and message.text.endswith("курс")
)
async def select_course(message: Message):
    course = message.text[0]  # "1 курс" → "1"

    await message.answer(
        "Выберите группу курса:",
        reply_markup=keyboards.groups_keyboard(course)
    )