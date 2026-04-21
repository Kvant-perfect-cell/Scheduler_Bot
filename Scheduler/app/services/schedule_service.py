from app.models.schedule import Schedule, Lesson
from app.data.parser.parser import parse_schedule, get_today_timestamp

def get_schedule_for_today(group: str) -> Schedule:
    timestamp = get_today_timestamp()
    raw_data = parse_schedule(group, timestamp)

    return raw_data