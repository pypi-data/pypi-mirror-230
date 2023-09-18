#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
some datetime utils
"""


import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY


utcnow = datetime.utcnow()
"""current utcnow datetime object"""
one_week_ago = datetime.utcnow() - relativedelta(weeks=1)
"""one_week_ago datetime object"""
one_day_ago = datetime.utcnow() - relativedelta(days=1)
"""one day ago datetime object"""
two_day_ago = datetime.utcnow() - relativedelta(days=2)
"""two day ago datetime object"""
one_hour_ago = datetime.utcnow() - relativedelta(hours=1)
"""one hour ago datetime object"""
one_month_ago = datetime.utcnow() - relativedelta(months=1)
"""one month ago datetime object"""


def dt_to_timestamp(dt, multiplier=1):
    """
    change datetime object to timestamp
    """
    timestamp = dt.timestamp()

    timestamp = timestamp * multiplier

    return int(timestamp)


def get_datetime_range(months):
    """
    return a list of datetime range, start from current time, and
    counted upon previous some months.
    """
    now = datetime.utcnow()
    sdt = now - relativedelta(months=months)
    return list(rrule(freq=MONTHLY, dtstart=sdt, until=now))


def get_dt_fromtimestamp(timestamp, utc=False, multiplier=1):
    """
    get datetime object from timestamp
    """

    if isinstance(timestamp, str):
        timestamp = float(timestamp)

    timestamp = timestamp * multiplier

    if utc:
        dt = datetime.utcfromtimestamp(timestamp)
    else:
        dt = datetime.fromtimestamp(timestamp)

    return dt


def get_timestamp(multiplier=1):
    """
    get current timestamp
    :return:
    """
    timestamp = time.time()

    timestamp = timestamp * multiplier

    return int(timestamp)


def is_same_year(dt1: datetime, dt2: datetime):
    """
    is the two datetime objects are in the same year
    """
    if dt1.year == dt2.year:
        return True
    else:
        return False


def is_same_month(dt1, dt2):
    """
    is the two datetime objects are in the same month
    """
    if (dt1.year == dt2.year) and (dt1.month == dt2.month):
        return True
    else:
        return False


def is_same_day(dt1, dt2):
    """
    is the two datetime objects are in the same day
    """
    if (dt1.year == dt2.year) and (dt1.month == dt2.month) and (dt1.day == dt2.day):
        return True
    else:
        return False


def is_same_hour(dt1, dt2):
    """
    is the two datetime objects are in the same hour
    """
    if (
        (dt1.year == dt2.year)
        and (dt1.month == dt2.month)
        and (dt1.day == dt2.day)
        and (dt1.hour == dt2.hour)
    ):
        return True
    else:
        return False


def normal_format_now():
    """
    get current normal format for now: '2018-12-21 15:39:20'
    :return:
    """
    return datetime.now().__format__("%Y-%m-%d %H:%M:%S")


def normal_format_utcnow():
    """
    get current normal format for utcnow: '2018-12-21 15:39:20'
    :return:
    """
    return datetime.utcnow().__format__("%Y-%m-%d %H:%M:%S")


def round_to_day(dt):
    """
    round a datetime object to day
    """
    res = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return res


def round_to_hour(dt):
    """
    round a datetime object to hour
    :param dt:
    :return:
    """
    res = dt.replace(minute=0, second=0, microsecond=0)
    return res


def round_to_minute(dt):
    """
    round a datetime object to minute
    """
    res = dt.replace(second=0, microsecond=0)
    return res


def round_to_second(dt):
    """
    round a datetime object to second
    """
    res = dt.replace(microsecond=0)
    return res
