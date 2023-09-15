from datetime import datetime, timedelta, date, time
import time as time_module

SECONDS_PER_DAY = int(timedelta(days=1).total_seconds())
SECONDS_PER_HOUR = int(timedelta(hours=1).total_seconds())
SECONDS_PER_MINUTE = int(timedelta(minutes=1).total_seconds())


def to_timestamp(val: datetime, unit='second'):
    if not val:
        return None
    return int(val.timestamp() * 1000) if unit == 'millisecond' else int(val.timestamp())


def strftime(t: datetime = None, f='%Y-%m-%d %H:%M:%S'):
    if not t:
        t = datetime.now()
    return t.strftime(f)


def strptime(date_string, f='%Y-%m-%d %H:%M:%S'):
    return datetime.strptime(date_string, f)


def get_end_time_of_day(day_delta=0):
    return datetime.combine(date.today(), time.max) + timedelta(days=day_delta)


def get_begin_time_of_day(day_delta=0):
    return datetime.combine(date.today(), time.min) + timedelta(days=day_delta)


def current_milli_time():
    return round(time_module.time() * 1000)


def current_sec_time():
    return round(time_module.time())


# string float
def fromtimestamp_in_milli(t) -> datetime:
    if not isinstance(t, int):
        t = int(t)
    return datetime.fromtimestamp(t // 1000)


def fromtimestamp_in_sec(t) -> datetime:
    if not isinstance(t, int):
        t = int(t)
    return datetime.fromtimestamp(t)
