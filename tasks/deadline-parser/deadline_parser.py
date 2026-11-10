"""Narrow bounty deadline grammar for agentswarm.space's importer.

Implements only the forms listed in SPEC.md; any other input returns None.
Standard library only, no wall clock, no network.
"""
import re
from datetime import datetime, timedelta, timezone

_MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}

_MONTH_DAY = re.compile(r'([a-z]{3}) (\d{1,2}) (\d{2}):(\d{2}) utc')
_ISO = re.compile(
    r'(\d{4})-(\d{2})-(\d{2})t(\d{2}):(\d{2})(?::(\d{2}))?(z|[+-]\d{2}:\d{2})'
)
_IN_DAYS = re.compile(r'in (\d+) days')


def _valid_date(year, month, day):
    try:
        datetime(year, month, day)
    except ValueError:
        return None
    return year, month, day


def _format_utc(dt):
    return '%04d-%02d-%02dT%02d:%02d:%02dZ' % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def _to_utc(now):
    if now.tzinfo is None:
        return now
    return now.astimezone(timezone.utc)


def _parse_month_day(match, now):
    month = _MONTHS.get(match.group(1))
    if month is None:
        return None
    day = int(match.group(2))
    hour = int(match.group(3))
    minute = int(match.group(4))
    if hour > 23 or minute > 59:
        return None
    if _valid_date(now.year, month, day) is None:
        return None
    try:
        candidate = datetime(now.year, month, day, hour, minute, tzinfo=timezone.utc)
    except ValueError:
        return None
    if candidate < now:
        if _valid_date(now.year + 1, month, day) is None:
            return None
        candidate = datetime(now.year + 1, month, day, hour, minute,
                             tzinfo=timezone.utc)
    return _format_utc(candidate)


def _parse_iso(match, now):
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    hour = int(match.group(4))
    minute = int(match.group(5))
    second = int(match.group(6)) if match.group(6) is not None else 0
    zone = match.group(7)
    if _valid_date(year, month, day) is None:
        return None
    if hour > 23 or minute > 59 or second > 59:
        return None
    if zone == 'z':
        tz = timezone.utc
    else:
        sign = 1 if zone[0] == '+' else -1
        offset_hours = int(zone[1:3])
        offset_minutes = int(zone[4:6])
        if offset_hours > 23 or offset_minutes > 59:
            return None
        tz = timezone(sign * timedelta(hours=offset_hours, minutes=offset_minutes))
    try:
        moment = datetime(year, month, day, hour, minute, second, tzinfo=tz)
    except ValueError:
        return None
    try:
        utc_moment = moment.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        return None
    return _format_utc(utc_moment)


def _parse_in_days(match, now):
    digits = match.group(1).lstrip('0') or '0'
    if len(digits) > 4:
        return None
    days = int(digits)
    if days > 3650:
        return None
    try:
        target = now + timedelta(days=days)
    except OverflowError:
        return None
    return _format_utc(target)


def _parse_end_of_week(now):
    try:
        sunday = now.date() + timedelta(days=(6 - now.weekday()))
        moment = datetime(sunday.year, sunday.month, sunday.day, 23, 59, 59,
                          tzinfo=timezone.utc)
    except (OverflowError, ValueError):
        return None
    return _format_utc(moment)


def parse_deadline(text, now):
    if not isinstance(text, str):
        return None
    stripped = text.strip()
    lowered = stripped.lower()
    if not lowered or lowered == 'none':
        return None
    current = _to_utc(now)

    match = _MONTH_DAY.fullmatch(lowered)
    if match:
        return _parse_month_day(match, current)

    match = _ISO.fullmatch(lowered)
    if match:
        return _parse_iso(match, current)

    match = _IN_DAYS.fullmatch(lowered)
    if match:
        return _parse_in_days(match, current)

    if lowered == 'end of week':
        return _parse_end_of_week(current)

    return None
