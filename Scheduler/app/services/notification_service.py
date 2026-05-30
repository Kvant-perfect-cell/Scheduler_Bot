notifications = []

def add_notification(user_id, group, lesson, minutes_before):
    notifications.append({
        "user_id": user_id,
        "group": group,
        "lesson": lesson,
        "minutes_before": minutes_before
    })

def get_notifications():
    return notifications

def delete_notification(index):
    if 0 <= index < len(notifications):
        notifications.pop(index)