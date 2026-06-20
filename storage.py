import json
import os


DATA_FILE = os.environ.get(
    "FIRE_VOLUNTEER_DATA_FILE",
    os.path.join(os.path.expanduser("~"), ".fire_volunteer.json"),
)


DEFAULT_DATA = {
    "volunteers": {},
    "schedules": {},
    "checkins": {},
}


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "volunteers": {},
            "schedules": {},
            "checkins": {},
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {
            "volunteers": {},
            "schedules": {},
            "checkins": {},
        }
    if "volunteers" not in data:
        data["volunteers"] = {}
    if "schedules" not in data:
        data["schedules"] = {}
    if "checkins" not in data:
        data["checkins"] = {}
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
