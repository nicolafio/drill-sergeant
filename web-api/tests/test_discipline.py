from datetime import datetime, date, time

from http import HTTPStatus
from icalendar import Calendar, Event

import responses

MOCK_SCHEDULE_URL = "https://example.com/schedule.ics"
MOCK_DAY_1 = date(2024, 3, 18)
MOCK_DAY_2 = date(2024, 3, 19)

def _get_mock_schedule_ical():
    schedule = Calendar()

    summaries = ["Task 1", "Task 2 ✓✓", "Task 3 ✓✓✓"]
    task_dates = [MOCK_DAY_1, MOCK_DAY_1, MOCK_DAY_2]
    start_times = [time(8, 0), time(9, 0), time(3, 0)]
    end_times = [time(9, 0), time(10, 0), time(4, 0)]

    properties = zip(summaries, task_dates, start_times, end_times)

    for summary, day, start, end in properties:
        task = Event()
        task.add("summary", summary)
        task.add("dtstart", datetime.combine(day, start))
        task.add("dtend", datetime.combine(day, end))
        schedule.add_component(task)

    return schedule.to_ical()

MOCK_SCHEDULE_ICAL = _get_mock_schedule_ical()

def test_get_discipline_ical(data, client, mocked_responses):
    data.clear()

    root_put = client.put("/v1/user/root")
    root_key = root_put.json["auth_key"]
    root_auth = ("root", root_key)

    user_info = {"schedule": MOCK_SCHEDULE_URL}
    user_put = client.put("/v1/user/user", auth = root_auth, json = user_info)
    user_key = user_put.json["auth_key"]

    mocked_responses.get(
        MOCK_SCHEDULE_URL,
        body = MOCK_SCHEDULE_ICAL,
        status = HTTPStatus.OK,
        content_type = "text/calendar"
    )

    response = client.get("/v1/user/user/discipline.ics", auth = ("user", user_key))

    assert response.status_code == HTTPStatus.OK
    assert response.mimetype == "text/calendar"
