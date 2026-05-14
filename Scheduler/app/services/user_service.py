user_groups = {}
temp_groups = {}

def set_user_group(user_id: int, group: str):
    user_groups[user_id] = group

def get_user_group(user_id: int):
    return user_groups.get(user_id)

def set_temp_group(user_id: int, group: str):
    temp_groups[user_id] = group

def get_temp_group(user_id: int):
    return temp_groups.get(user_id)