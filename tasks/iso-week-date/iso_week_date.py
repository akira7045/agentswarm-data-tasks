"""ISO week date -> calendar date (ISO 8601), stdlib only."""
import datetime


def _is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _weeks_in_iso_year(year):
    jan1 = datetime.date(year, 1, 1).weekday()
    if jan1 == 3:
        return 53
    if jan1 == 2 and _is_leap(year):
        return 53
    return 52


def iso_week_date(year, week, day):
    if type(year) is not int:
        raise TypeError("year must be int")
    if type(week) is not int:
        raise TypeError("week must be int")
    if type(day) is not int:
        raise TypeError("day must be int")

    if not (1 <= year <= 9999):
        raise ValueError("year out of range")
    if not (1 <= week <= 53):
        raise ValueError("week out of range")
    if not (1 <= day <= 7):
        raise ValueError("day out of range")
    if week == 53 and _weeks_in_iso_year(year) != 53:
        raise ValueError("year has no week 53")

    jan4 = datetime.date(year, 1, 4)
    week1_monday = jan4 - datetime.timedelta(days=jan4.weekday())
    ordinal = week1_monday.toordinal() + (week - 1) * 7 + (day - 1)
    try:
        target = datetime.date.fromordinal(ordinal)
    except (OverflowError, ValueError):
        raise ValueError("resulting date out of range")
    if not (1 <= target.year <= 9999):
        raise ValueError("resulting date out of range")
    return "%04d-%02d-%02d" % (target.year, target.month, target.day)
