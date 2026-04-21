from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.bot.keyboards import keyboards
from app.services.schedule_service import get_schedule_for_today
from app.services.user_service import set_user_group, get_user_group

router = Router()

user_groups = {}

LESSON_TIMES = {
    1: "08:30 - 9:50",
    2: "10:00 - 11:20",
    3: "12:10 - 13:30",
    4: "13:40 - 15:00",
    5: "15:10 - 16:30",
    6: "16:40 - 18:00",
}

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Выбери действие 👇",
        reply_markup=keyboards.main_keyboard()
    )

@router.message(lambda message: message.text == "📅 Сегодня")
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
        print(lesson["time"])

    for lesson in schedule:
        time = LESSON_TIMES.get(lesson["time"], str(lesson["time"]))
        subject = lesson["subject"]
        teacher = lesson["teacher"]

        text += f"{time}\n{subject}\n👨‍🏫 {teacher}\n\n"

    for part in split_message(text):
        await message.answer(part)

@router.message(Command("setgroup"))
async def set_group_handler(message: Message):
    try:
        group = message.text.split()[1]
        set_user_group(message.from_user.id, group)
        await message.answer(f"Группа сохранена: {group}")
    except:
        await message.answer("Используй: /setgroup 501")
