from aiogram import Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from html import escape
from datetime import datetime, timedelta

from app.bot.keyboards import keyboards
from app.services.user_service import set_user_group, get_user_group, set_temp_group, get_temp_group
from app.services.notification_service import add_notification, get_notifications, delete_notification
from app.data.parser.parser import get_base_info, parse_schedule, get_today_timestamp
from app.utils.date_utils import format_date
from app.config.config import get_lesson_times
from datetime import datetime, timedelta

LESSON_TIMES = get_lesson_times()

user_groups = {}
user_notify_lesson = {}

router = Router()

changing_group = set()

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
        time = get_lesson_times().get(lesson["time"], str(lesson["time"]))
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
@router.message(lambda m: m.text and m.text.isdigit())
async def handle_numbers(message: Message):
    user_id = message.from_user.id

    # если это ввод для напоминаний
    if user_id in user_notify_lesson:
        minutes = int(message.text)

        if not (5 <= minutes <= 60):
            await message.answer("Введи число от 5 до 60")
            return

        lesson = user_notify_lesson[user_id]
        lesson_time = get_lesson_times()[lesson]

        start_time = datetime.strptime(
        lesson_time.split(" - ")[0],
        "%H:%M"
        )

        notify_time = (
            datetime.combine(datetime.today(), start_time.time())
            - timedelta(minutes=minutes)
        ).strftime("%H:%M")

        

        await message.answer(
            f"✅ Напомню за {minutes} минут до начала {lesson} пары.\n"
            f"⏰ Время напоминания: {notify_time}",
            reply_markup=keyboards.main_keyboard()
        )

        lesson = user_notify_lesson[user_id]
        group = get_user_group(user_id)

        add_notification(
            user_id=user_id,
            group=group,
            lesson=lesson,
            minutes_before=minutes
        )
        
        del user_notify_lesson[user_id]
        return

    # иначе это выбор группы
    group = message.text
    bot_message = await message.answer(f"Группа выбрана: {group}, готовим расписание...")

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
        await callback.message.edit_text(
            "Сегодня пар нет", 
             reply_markup=keyboards.main_keyboard()
        )
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

# НАПОМИНАНИЯ

@router.callback_query(lambda c: c.data == "notifications")
async def notifications_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Управление напоминаниями 👇",
        reply_markup=keyboards.notifications_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "notifications_add")
async def notifications_add(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери пару 👇",
        reply_markup=keyboards.lessons_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("notify_lesson:"))
async def select_lesson(callback: CallbackQuery):
    lesson = int(callback.data.split(":")[1])

    user_notify_lesson[callback.from_user.id] = lesson

    await callback.message.edit_text(
        "Введи за сколько минут напомнить (5-60):"
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "notifications_list")
async def notifications_list(callback: CallbackQuery):
    user_id = callback.from_user.id

    all_notifications = get_notifications()

    user_notifications = [
        n for n in all_notifications
        if n["user_id"] == user_id
    ]

    if not user_notifications:
        await callback.message.edit_text(
            "📋 У тебя нет активных напоминаний.",
            reply_markup=keyboards.notifications_menu_keyboard()
        )
        return

    text = "📋 Активные напоминания:\n\n"

    for i, n in enumerate(user_notifications, start=1):
        text += (
            f"{i}. Пара {n['lesson']} "
            f"(за {n['minutes_before']} мин.)\n"
        )

    await callback.message.edit_text(
    text,
    reply_markup=keyboards.notification_list_keyboard(
        all_notifications,
        user_id
        )
    )

    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("delete_notify:"))
async def delete_notification_handler(callback: CallbackQuery):
    index = int(callback.data.split(":")[1])

    delete_notification(index)

    await callback.answer("Напоминание удалено ✅")

    await notifications_list(callback)

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
