from aiogram import Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from html import escape
from datetime import datetime, timedelta

from app.bot.keyboards import keyboards
from app.services.user_service import set_user_group, get_user_group, set_temp_group, get_temp_group
from app.data.parser.parser import get_base_info, parse_schedule, get_today_timestamp
from app.utils.date_utils import format_date

router = Router()

user_groups = {}

changing_group = set()

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

def format_schedule(group, date, lessons):
    text = (
        f"<b>Расписание</b>\n"
        f"<b>Группа:</b> <code>{escape(str(group))}</code>\n"
        f"<b>Дата:</b> {escape(format_date(date))}\n\n"
    )

    for lesson in lessons:
        lesson_number = lesson.get("number_lesson", lesson["time"])
        time = LESSON_TIMES.get(lesson["time"], str(lesson["time"]))
        subject = escape(lesson["subject"])
        teacher = escape(lesson["teacher"])

        subgroup = ""
        if lesson.get("subgroup") and lesson.get("subgroup") != 0:
            subgroup = f"\n<b>Подгруппа:</b> {escape(str(lesson.get('subgroup')))}"

        cabinet = escape(str(lesson.get("cabinet") or "Не указан"))

        text += (
            f"<b>{lesson_number} пара</b>  <code>{escape(time)}</code>\n"
            f"{subject}\n"
            f"<b>Преподаватель:</b> {teacher}{subgroup}\n"
            f"<b>{cabinet}</b>\n"
            f"━━━━━━━━━━━━━━\n"
        )

    return text
    

# НАЧАЛЬНОЕ ОКНО

# /start
@router.message(Command("start"))
async def start_handler(message: Message):
    get_base_info()
    msg = await message.answer(
        "Обновляю интерфейс…",
        reply_markup=ReplyKeyboardRemove()
    )
    await msg.delete()
    
    group = get_user_group(message.from_user.id)

    await message.answer(
        "Привет! Выбери действие 👇",
        reply_markup=keyboards.main_keyboard(group),
    )

# КНОПКОЙ
@router.callback_query(lambda c: c.data == ("back_to_main"))
async def start_handler_callback(callback: CallbackQuery):
    group = get_user_group(callback.from_user.id)
    print("Back to main, getting user temp group:", group, "main:", get_user_group(callback.from_user.id))

    await callback.message.edit_text(
        "Выбери действие 👇",
        reply_markup=keyboards.main_keyboard(group)
    )

# ОКНО ПОСЛЕ НАЧАТИЯ "Выбрать группу"

@router.callback_query(lambda c: c.data.startswith("courses"))
async def select_group_callback(callback: CallbackQuery):

    await callback.message.edit_text(
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
async def select_course_callback(callback: CallbackQuery):
    course = callback.data.split(":")[1]

    await callback.message.edit_text(
        "Выбери группу 👇",
        reply_markup=keyboards.groups_inline_keyboard(course)
    )

    await callback.answer()

# ОКНО ПОСЛЕ ВЫБОРА ГРУППЫ

# ТЕКСТОМ
@router.message(lambda message: message.text and message.text.isdigit())
async def group_selected(message: Message):
    group = message.text
    bot_message = await message.answer(f"Группа выбрана: {group}, готовим расписание...")

    user_id = message.from_user.id

    set_temp_group(user_id, group)

    if user_id in changing_group:
        set_user_group(user_id, group)
        changing_group.remove(user_id)

    schedule = parse_schedule(group, get_today_timestamp())
    if not schedule:
        await bot_message.edit_text(
            "Для этой группы нет расписания",
            reply_markup=keyboards.back_keyboard()
        )
        return

    await bot_message.edit_text(
        f"Группа {group}, Выбери день 👇",
        reply_markup=keyboards.days_keyboard(schedule.keys())
    )

# КНОПКОЙ
@router.callback_query(lambda c: c.data.startswith("group:"))
async def group_selected_callback(callback: CallbackQuery):
    group = callback.data.split(":")[1]

    user_id = callback.from_user.id
    set_temp_group(user_id, group)

    if user_id in changing_group:
        set_user_group(user_id, group)
        changing_group.remove(user_id)

    await callback.message.edit_text(
        f"Группа выбрана: {group}, готовим расписание..."
    )
    
    schedule = parse_schedule(group, get_today_timestamp())
    if not schedule:
        await callback.message.edit_text(
            "Для этой группы нет расписания",
            reply_markup=keyboards.back_keyboard()
        )
        return

    await callback.message.edit_text(
        f"Группа {group}, Выбери день 👇",
        reply_markup=keyboards.days_keyboard(schedule.keys())
    )

    await callback.answer()

# ВЫБОР ДНЯ

@router.callback_query(lambda c: c.data.startswith("day:"))
async def day_selected(callback: CallbackQuery):
    date = callback.data.split(":")[1]

    group = get_temp_group(callback.from_user.id)

    schedule = parse_schedule(group, get_today_timestamp())
    lessons = schedule.get(date)

    if not lessons:
        await callback.message.edit_text("На этот день пар нет")
        return

    text = format_schedule(group, date, lessons)

    parts = split_message(text)

    await callback.message.edit_text(
        parts[0],
        parse_mode="HTML",
        reply_markup=keyboards.back_to_days_keyboard()
    )

    for part in parts[1:]:
        await callback.message.answer(part, parse_mode="HTML")

    await callback.answer()

# ВЗАИМОДЕЙСВИЯ С ГРУППОЙ
@router.callback_query(lambda c: c.data == "my_group")
async def my_group_handler(callback: CallbackQuery):
    group = get_user_group(callback.from_user.id)

    if not group:
        changing_group.add(callback.from_user.id)   
        set_user_group(callback.from_user.id, None)
        set_temp_group(callback.from_user.id, None)

        await callback.message.edit_text(
            "Выберите группу 👇",
            reply_markup=keyboards.courses_inline_keyboard()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"Твоя группа: <code>{group}</code>\nВыбери действие 👇",
        parse_mode="HTML",
        reply_markup=keyboards.my_group_actions_keyboard()
    )

    await callback.answer()

# СМЕНА ГРУППЫ
@router.callback_query(lambda c: c.data == "change_group")
async def change_group(callback: CallbackQuery):
    changing_group.add(callback.from_user.id)   
    set_user_group(callback.from_user.id, None)
    set_temp_group(callback.from_user.id, None)


    await callback.message.edit_text(
        "Выберите новую группу 👇",
        reply_markup=keyboards.courses_inline_keyboard()
    )

    await callback.answer()

# РАСПИСАНИЕЙ СВОЕЙ ГРУППЫ
@router.callback_query(lambda c: c.data == "my_full")
async def my_full(callback: CallbackQuery):
    group = get_user_group(callback.from_user.id)

    schedule = parse_schedule(group, get_today_timestamp())

    await callback.message.edit_text(
        "Выбери день 👇",
        reply_markup=keyboards.days_keyboard(schedule.keys())
    )

    await callback.answer()

# РАСПИСАНИЕ СВОЕЙ ГРУППЫ СЕГОДНЯ
@router.callback_query(lambda c: c.data == "my_today")
async def my_today(callback: CallbackQuery):
    group = get_user_group(callback.from_user.id)

    from app.data.parser.parser import parse_schedule, get_today_timestamp

    schedule = parse_schedule(group, get_today_timestamp())

    today = str(datetime.now().date())
    lessons = schedule.get(today)

    if not lessons:
        await callback.message.edit_text("Сегодня пар нет")
        return

    text = format_schedule(group, today, lessons)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboards.back_to_days_keyboard()
    )

    await callback.answer()

# РАСПИСАНИЕ СВОЕЙ ГРУППЫ ЗАВТРА
@router.callback_query(lambda c: c.data == "my_tomorrow")
async def my_tomorrow(callback: CallbackQuery):
    group = get_user_group(callback.from_user.id)

    from app.data.parser.parser import parse_schedule, get_today_timestamp

    schedule = parse_schedule(group, get_today_timestamp())

    tomorrow = str((datetime.now() + timedelta(days=1)).date())
    lessons = schedule.get(tomorrow)

    if not lessons:
        await callback.message.edit_text("Завтра пар нет")
        return

    text = format_schedule(group, tomorrow, lessons)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboards.back_to_days_keyboard()
    )

    await callback.answer()

# Кнопки Назад

@router.callback_query(lambda c: c.data == "back_to_days")
async def back_to_days(callback: CallbackQuery):
    group = get_temp_group(callback.from_user.id)

    schedule = parse_schedule(group, get_today_timestamp())

    if not schedule:
        await callback.message.edit_text("Нет доступных дней")
        return
    
    await callback.message.edit_text(
        f"Группа {group}, Выбери день 👇",
        reply_markup=keyboards.days_keyboard(schedule.keys())
    )

    await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_courses")
async def back_to_courses(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=keyboards.courses_inline_keyboard()
    )
    await callback.answer()
