from aiogram import Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from html import escape

from app.bot.keyboards import keyboards
from app.services.schedule_service import get_schedule_for_today
from app.services.user_service import set_user_group, get_user_group
from app.data.parser.parser import get_base_info

router = Router()

user_groups = {}

LESSON_TIMES = {
    1: "08:30 - 9:50",
    2: "10:00 - 11:20",
    3: "12:10 - 13:30",
    4: "13:40 - 15:00",
    5: "15:10 - 16:30",
    6: "16:40 - 18:00",
    7: "18:10 - 19:30",
    8: "19:40 - 21:00",
}

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def return_schedule(group):
    schedule = get_schedule_for_today(group)

    if not schedule:
        return False

    text = f"<b>Расписание на сегодня</b>\n<b>Группа:</b> <code>{escape(str(group))}</code>\n\n"

    for lesson in schedule:
        lesson_number = lesson.get("number_lesson", lesson["time"])
        time = LESSON_TIMES.get(lesson["time"], str(lesson["time"]))
        subject = escape(lesson["subject"])
        teacher = escape(lesson["teacher"])
        subgroup = ""
        if lesson.get("subgroup") != 0:
            subgroup = f"\n<b>Подгруппа:</b> {escape(str(lesson.get('subgroup')))}"
        cabinet = escape(str(lesson.get("cabinet") or "Не указан"))


        text += (
            f"<b>{lesson_number} пара</b>  <code>{escape(time)}</code>\n"
            f"{subject}\n"
            f"<b>Преподаватель:</b> {teacher}{subgroup}\n"
            f"<b>{cabinet}</b> \n"
            f"━━━━━━━━━━━━━━\n"
        )
        
    return text
    

# НАЧАЛЬНОЕ ОКНО

@router.message(Command("start"))
async def start_handler(message: Message):
    get_base_info()
    msg = await message.answer(
        "Обновляю интерфейс…",
        reply_markup=ReplyKeyboardRemove()
    )
    await msg.delete()
    
    await message.answer(
        "Привет! Выбери действие 👇",
        reply_markup=keyboards.main_keyboard(),
    )


# @router.message(lambda message: message.text == "Расписание на сегодня")
# async def today_button_handler(message: Message):
#     group = get_user_group(message.from_user.id)

#     if not group:
#         await message.answer("Сначала установи группу: /setgroup 501")
#         return

#     schedule = get_schedule_for_today(group)

#     if not schedule:
#         await message.answer("🎉 Сегодня пар нет!")
#         return

#     text = f"📅 Сегодня ({group}):\n\n"

#     for lesson in schedule:
#         time = LESSON_TIMES.get(lesson["time"], str(lesson["time"]))
#         subject = lesson["subject"]
#         teacher = lesson["teacher"]

#         text += f"{time}\n{subject}\n👨‍🏫 {teacher}\n\n"

#     for part in split_message(text):
#         await message.answer(part)

# @router.message(lambda message: message.text == "Выбрать группу")
# async def select_group(message: Message):
   
#     await message.answer(
#         "Выберите курс:",
#         reply_markup=keyboards.courses_keyboard()
#     )

# ОКНО ПОСЛЕ НАЧАТИЯ "Выбрать группу"

@router.callback_query(lambda c: c.data.startswith("courses"))
async def group_selected(callback: CallbackQuery):

    await callback.message.answer(
        "Сначала выбери курс 👇",
        reply_markup=keyboards.courses_inline_keyboard()
    )

    await callback.answer()

# ОКНО ПОСЛЕ ВЫБОРА КУРСА

# ТЕКСТОМ
@router.message(lambda message: message.text and message.text.endswith("курс"))
async def select_course(message: Message):
    course = message.text[0]

    await message.answer(
        "Выберите группу:",
        reply_markup=keyboards.groups_inline_keyboard(course)
    )

# КНОПКОЙ
@router.callback_query(lambda c: c.data.startswith("course:"))
async def group_selected(callback: CallbackQuery):
    course = callback.data.split(":")[1]

    await callback.message.answer(
        "Выбери группу 👇",
        reply_markup=keyboards.groups_inline_keyboard(course)
    )

    await callback.answer()

# ОКНО ПОСЛЕ ВЫБОРА ГРУППЫ

# ТЕКСТОМ
@router.message(lambda message: message.text and message.text.isdigit())
async def group_selected_text(message: Message):
    group = message.text
    await message.answer(f"Группа выбрана: {group}, готовим расписание...")

    text = return_schedule(group)

    if text == False:
        await message.answer("Для этой группы пар нет/такой группы не существует",
            reply_markup=keyboards.main_keyboard_text())
        return

    for part in split_message(text):
        await message.answer(part, parse_mode="HTML")

# КНОПКОЙ
@router.callback_query(lambda c: c.data.startswith("group:"))
async def group_selected(callback: CallbackQuery):
    group = callback.data.split(":")[1]

    # set_user_group(callback.from_user.id, group)

    await callback.message.edit_text(
        f"Группа выбрана: {group}, готовим расписание..."
    )
    
    text = return_schedule(group)

    if text == False:
        await callback.message.answer("Для этой группы пар нет/такой группы не существует",
            reply_markup=keyboards.main_keyboard())
        return

    for part in split_message(text):
        await callback.message.answer(
            part,
            parse_mode="HTML",
            reply_markup=keyboards.main_keyboard())

    await callback.answer()

# @router.callback_query(lambda c: c.data == "back_to_main")
# async def back_to_courses(callback: CallbackQuery):
#     await callback.message.edit_text(
#         "Выберите курс:",
#         reply_markup=keyboards.main_keyboard()
#     )
#     await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_courses")
async def back_to_courses(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=keyboards.courses_inline_keyboard()
    )
    await callback.answer()
