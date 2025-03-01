import re

def group_number_validator(group_number):
    group_number = str(group_number)
    pattern = r'^[А-Я]{4}-\d{2}-\d{2}$'
    if re.match(pattern, group_number):
        return str(group_number)
    else:
        return False

def date_validator(date):
    date = str(date)
    pattern = r'^[А-Я][а-я]+, \d{4}, \d{1,2}$'
    if re.match(pattern, date):
        return str(date)
    else:
        return False