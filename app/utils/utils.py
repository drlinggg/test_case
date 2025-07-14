from datetime import time

def str_to_time(time_str: str) -> time:
    hours, minutes = map(int, time_str.split(':'))
    return time(hour=hours, minute=minutes)

def time_to_str(t: time) -> str:
    return t.strftime("%H:%M")

