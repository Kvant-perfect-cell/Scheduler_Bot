user_groups = {}

def set_user_group(user_id: int, group: str):
    user_groups[user_id] = group

def get_user_group(user_id: int):
    return user_groups.get(user_id)