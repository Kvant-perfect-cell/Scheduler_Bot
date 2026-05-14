import requests
from datetime import datetime, timedelta
import time

BASE_URL = "https://surpk.ru/api/schedule"

base_info = 0
dictionaries_data = 0
schedule_cache = None
schedule_cache_time = None
CACHE_TTL = 1800  # 30 минут
parsed_cache = {}

def get_base_info():
    global base_info

    if base_info == 0:
        url = f"{BASE_URL}/index"
        response = requests.get(url)
        data = response.json()

        base_info = data["baseInfo"]["data"]

    return base_info

def build_dict(items):
    return {item["id"]: item["name"] for item in items}

def get_dictionaries():
    global dictionaries_data

    if dictionaries_data == 0:
        base = get_base_info()
        dictionaries_data = {
            "groups": build_dict(base["groups"]),
            "teachers": build_dict(base["teachers"]),
            "disciplines": build_dict(base["disciplines"]),
            "audithories": build_dict(base["audithories"]),
        }
    
    return dictionaries_data

def get_schedule_raw(timestamp):
    global schedule_cache, schedule_cache_time

    now = datetime.now().timestamp()

    if schedule_cache and schedule_cache_time:
        if now - schedule_cache_time < CACHE_TTL:
            return schedule_cache

    url = f"{BASE_URL}/schedule"
    response = requests.get(url, params={"date": timestamp})

    data = response.json()["schedule"]["data"]["schedule"]

    schedule_cache = data
    schedule_cache_time = now

    return data

def get_today_timestamp():
    today = datetime.now()
    return int(today.timestamp() * 1000)

def get_available_groups():
    dictionaries = get_dictionaries()

    groups = dictionaries["groups"]
    return groups

def get_groups_by_courses():
    dictionaries = get_dictionaries()

    groups = dictionaries["groups"]
    courses = {}
    newest_course = 0
    for id, group in groups.items():
        course = int(group[0])*100
        if course not in courses:
            courses[course] = [group]
            if course > newest_course:
                newest_course = course
        else:
            courses[course].append(group)
    
    return courses, newest_course

def parse_schedule(group_name: str, timestamp: int):
    global parsed_cache

    cache_key = f"{group_name}"
    now = time.time()

    if cache_key in parsed_cache:
        data, saved_time = parsed_cache[cache_key]

        if now - saved_time < CACHE_TTL:
            return data

    dictionaries = get_dictionaries()
    
    groups = dictionaries["groups"]
    disciplines = dictionaries["disciplines"]
    teachers = dictionaries["teachers"]
    audithories = dictionaries["audithories"]

    group_id = None
    for gid, name in groups.items():
        if name == group_name:
            group_id = gid
            break

    if not group_id:
        return {}

    schedule_days = get_schedule_raw(timestamp)

    result = {}

    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())   # monday this week
    end = start + timedelta(days=13)                  # sunday next week

    for day in schedule_days:
        day_date = datetime.fromtimestamp(day["date"] / 1000).date()

        lessons = []

        for lesson in day["lessons"]:
            if lesson["group"] == group_id:
                lessons.append({
                    "number_lesson": lesson["number_lesson"],
                    "time": lesson["number_lesson"],
                    "subject": disciplines.get(lesson["discipline"], "Неизвестно"),
                    "teacher": teachers.get(lesson["teacher"], "Неизвестно"),
                    "subgroup": lesson.get("subgroup"),
                    "cabinet": audithories.get(lesson.get("auditoria"), "Неизвестно")
                })

        if lessons and (start <= day_date <= end):
            result[str(day_date)] = lessons

    parsed_cache[cache_key] = (result, now)
    return result