notifications = []

def add_notification(user_id, lesson, minutes_before):
    notifications.append({
        "user_id": user_id,
        "lesson": lesson,
        "minutes_before": minutes_before,
        "sent": False
    })

def get_notifications():
    return notifications

def delete_notification(index):
    if 0 <= index < len(notifications):
        notifications.pop(index)