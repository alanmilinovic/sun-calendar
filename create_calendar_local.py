import requests
from ics import Calendar, Event
from datetime import datetime, timezone, timedelta
import pytz

CALENDAR_NAME = "Sunrise and Sunset for Valencia"
CALENDAR_DESCRIPTION = "Sunrise and Sunset for Valencia"

def get_sun_events(current_date):
    # API call for sunrise and sunset times in Valencia, Spain
    sun_times_url = (
        f"https://api.sunrise-sunset.org/json"
        f"?lat=39.4699&lng=-0.3763&date={current_date}"
    )

    print(f"sun_times_url: {sun_times_url}")

    response = requests.get(sun_times_url)

    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return []

    data = response.json()
    print(f"response json: {data}")

    time_format = "%I:%M:%S %p"
    year, month, day = map(int, current_date.split("-"))

    datetime_objects = {
        key: datetime.strptime(value, time_format).replace(tzinfo=pytz.utc)
        for key, value in data["results"].items()
        if key != "day_length"
    }

    for key, dt_obj in datetime_objects.items():
        datetime_objects[key] = dt_obj.replace(
            year=year,
            month=month,
            day=day
        )

    events = []

    # Sunrise
    e = Event()
    e.name = "🌅 Sunrise"
    e.begin = datetime_objects["sunrise"]
    e.duration = timedelta(minutes=15)
    e.description = CALENDAR_DESCRIPTION
    events.append(e)

    # Sunset
    e = Event()
    e.name = "🌇 Sunset"
    e.begin = datetime_objects["sunset"]
    e.duration = timedelta(minutes=15)
    e.description = CALENDAR_DESCRIPTION
    events.append(e)

    return events


# Create calendar
c = Calendar()

# Calendar metadata
c.extra.append(("X-WR-CALNAME", CALENDAR_NAME))
c.extra.append(("X-WR-CALDESC", CALENDAR_DESCRIPTION))
c.extra.append(("X-WR-TIMEZONE", "Europe/Madrid"))

# Get today + next 6 days
current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

dates = [
    (datetime.now(timezone.utc) + timedelta(days=i)).strftime("%Y-%m-%d")
    for i in range(7)
]

for date in dates:
    for event in get_sun_events(date):
        c.events.add(event)

# Write ICS file
with open("sun.ics", "w", encoding="utf-8") as f:
    f.writelines(c.serialize_iter())
