import requests
from datetime import datetime

BASE_URL = "https://surpk.ru/api/schedule"

def get_base_info():
    url = f"{BASE_URL}/index"
    response = requests.get(url)
    data = response.json()

    return data["baseInfo"]["data"]

def build_dict(items):
    return {item["id"]: item["name"] for item in items}

def get_dictionaries():
    base = get_base_info()
    return {
        "groups": build_dict(base["groups"]),
        "teachers": build_dict(base["teachers"]),
        "disciplines": build_dict(base["disciplines"]),
        "audithories": build_dict(base["audithories"]),
    }

def get_schedule_raw(timestamp):
    url = f"{BASE_URL}/schedule"
    response = requests.get(url, params={"date": timestamp})

    print("STATUS:", response.status_code)
    print("TEXT:", response.text[:200])  # 🔥 это спасёт тебя

    data = response.json()

    return data["schedule"]["data"]["schedule"]

def get_today_timestamp():
    today = datetime.now()
    return int(today.timestamp() * 1000)

def get_available_groups():
    dictionaries = get_dictionaries()

    groups = dictionaries["groups"]
    return groups

def parse_schedule(group_name: str, timestamp: int):
    dictionaries = get_dictionaries()
    
    groups = dictionaries["groups"]
    disciplines = dictionaries["disciplines"]
    teachers = dictionaries["teachers"]

    # найти id группы по имени
    group_id = None
    for gid, name in groups.items():
        if name == group_name:
            group_id = gid
            break

    if not group_id:
        return []

    schedule_days = get_schedule_raw(timestamp)

    today = datetime.now().date()

    result = []

    for day in schedule_days:
        day_date = datetime.fromtimestamp(day["date"] / 1000).date()

        if day_date != today:
            continue  # 🔥 пропускаем не сегодня

        print(day["lessons"])
        for lesson in day["lessons"]:
            if lesson["group"] == group_id:
                result.append({
                    "time": lesson["number_lesson"],
                    "subject": disciplines.get(lesson["discipline"], "Неизвестно"),
                    "teacher": teachers.get(lesson["teacher"], "Неизвестно")
                })

    return result

if __name__ == "__main__":
    data = parse_schedule("418", 1776020400000)

    for lesson in data:
        print(lesson)