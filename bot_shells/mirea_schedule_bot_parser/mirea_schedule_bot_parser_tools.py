import re

def group_number_validator(group_number):
    group_number = str(group_number)
    pattern = r'^[А-Я]{4}-\d{2}-\d{2}$'
    if re.match(pattern, group_number):
        return str(group_number)
    else:
        return False