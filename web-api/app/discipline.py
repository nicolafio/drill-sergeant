from http import HTTPStatus
from datetime import datetime
from datetime import timedelta

from flask import Blueprint

import requests

from icalendar import Calendar, Event

from .auth import auth_key_required
from .user import user_existence_required
from .user import bp as user_bp
from .data import data

bp = Blueprint("discipline", __name__, url_prefix = user_bp.url_prefix)

PASS_GRADE = 40
EXCELLENT_GRADE = 70
OUTSTANDING_GRADE = 90
PERFECT_GRADE = 100

PASS_MARKS = PASS_GRADE
EXCELLENCE_MARKS = EXCELLENT_GRADE - PASS_GRADE
OUTSTANDING_MARKS = OUTSTANDING_GRADE - EXCELLENT_GRADE
PERFECT_MARKS = PERFECT_GRADE - OUTSTANDING_GRADE

HOURS_FOR_EXCELLENT_GRADE = 7
HOURS_FOR_OUTSTANDING_GRADE = 8
HOURS_FOR_PERFECT_GRADE = 9

def _get_duration_hours(ical_event):
    start = ical_event.get("dtstart").dt
    end = ical_event.get("dtend").dt

    return (end - start) / timedelta(hours = 1)

def _calculate_discipline_score(ical_events):
    total = len(ical_events)
    more_than_half = total // 2 + 1

    summaries = [e.get("summary") for e in ical_events]
    durations_hours = [_get_duration_hours(e) for e in ical_events]

    with_single_check = ["✓" in s for s in summaries]
    with_double_check = ["✓✓" in s for s in summaries]
    with_triple_check = ["✓✓✓" in s for s in summaries]

    with_single_check_count = sum(with_single_check)
    with_double_check_count = sum(with_double_check)
    with_triple_check_count = sum(with_triple_check)

    hours_with_single_check = sum(d for d, c in zip(durations_hours, with_single_check) if c)
    hours_with_double_check = sum(d for d, c in zip(durations_hours, with_double_check) if c)
    hours_with_triple_check = sum(d for d, c in zip(durations_hours, with_triple_check) if c)

    pass_factor = min(1, with_single_check_count / more_than_half)

    excellence_factor = (
        (with_single_check_count / total) *
        min(1, hours_with_single_check / HOURS_FOR_EXCELLENT_GRADE)
    )

    outstanding_factor = (
        excellence_factor *
        (with_double_check_count / total) *
        min(1, hours_with_double_check / HOURS_FOR_OUTSTANDING_GRADE)
    )

    perfection_factor = (
        outstanding_factor *
        (with_triple_check_count / total) *
        min(1, hours_with_triple_check / HOURS_FOR_PERFECT_GRADE)
    )

    score = PASS_MARKS * pass_factor
    score += EXCELLENCE_MARKS * excellence_factor
    score += OUTSTANDING_MARKS * outstanding_factor
    score += PERFECT_MARKS * perfection_factor

    return int(score)

def _get_events_by_day(ical_calendar):
    by_day = dict()

    for event in ical_calendar.walk("vevent"):
        day = event.get("dtstart").dt.strftime("%Y-%m-%d")

        if day not in by_day:
            by_day[day] = list()

        by_day[day].append(event)

    return by_day

@bp.route("/<user>/discipline.ics", methods = ["GET"])
@auth_key_required
@user_existence_required
def _get_discipline_ical(user):
    if "schedule" not in data["users"][user]:
        return {
            "type": "problems/no_schedule",
            "title": "No schedule",
            "detail": "The user has no schedule"
        }, HTTPStatus.NOT_FOUND

    # TODO: ensure that the URL is not calling internal services!
    response = requests.get(data["users"][user]["schedule"])

    if response.status_code != HTTPStatus.OK:
        return {
            "type": "problems/schedule_fetch_error",
            "title": "Schedule fetch error",
            "detail": "The schedule could not be fetched"
        }, HTTPStatus.BAD_GATEWAY

    if "text/calendar" not in response.headers["Content-Type"]:
        return {
            "type": "problems/invalid_schedule",
            "title": "Invalid schedule",
            "detail": "The schedule is not in iCalendar format"
        }, HTTPStatus.BAD_GATEWAY

    schedule_ical = response.text
    schedule_calendar = Calendar.from_ical(schedule_ical)
    discipline_calendar = Calendar()

    for day, events in _get_events_by_day(schedule_calendar).items():
        discipline_day = Event()
        discipline_day.add("dtstart", datetime.strptime(day, "%Y-%m-%d").date())

        score = _calculate_discipline_score(events)

        discipline_day.add("summary", str(score))
        discipline_calendar.add_component(discipline_day)

    discipline_ical = discipline_calendar.to_ical()

    return discipline_ical, HTTPStatus.OK, {"Content-Type": "text/calendar"}
