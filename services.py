from datetime import datetime

from models import (
    MAX_PER_SHIFT,
    validate_date,
    validate_month,
    validate_phone,
    validate_shift,
    validate_volunteer_id,
    validate_volunteer_type,
)
from storage import load_data, save_data


def add_volunteer(vid, name, phone, vtype):
    validate_volunteer_id(vid)
    validate_phone(phone)
    validate_volunteer_type(vtype)

    data = load_data()
    if vid in data["volunteers"]:
        raise ValueError(f"志愿者ID已存在：{vid}")

    data["volunteers"][vid] = {
        "id": vid,
        "name": name,
        "phone": phone,
        "type": vtype,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_data(data)
    return f"志愿者添加成功：{vid} {name}（{vtype}）"


def schedule_shift(vid, date_str, shift):
    validate_volunteer_id(vid)
    validate_date(date_str)
    validate_shift(shift)

    data = load_data()
    if vid not in data["volunteers"]:
        raise ValueError(f"志愿者ID不存在：{vid}")

    date_schedules = data["schedules"].setdefault(date_str, {})
    for s_key, s_list in date_schedules.items():
        if vid in s_list:
            raise ValueError(f"志愿者 {vid} 在 {date_str} 已排有 {s_key} 班次")

    shift_list = date_schedules.setdefault(shift, [])
    if len(shift_list) >= MAX_PER_SHIFT:
        raise ValueError(
            f"{date_str} {shift} 班次人数已达上限（{MAX_PER_SHIFT}人）"
        )

    if vid in shift_list:
        raise ValueError(f"志愿者 {vid} 在 {date_str} {shift} 已排班")

    shift_list.append(vid)
    save_data(data)
    return f"排班成功：{vid} {data['volunteers'][vid]['name']} {date_str} {shift}"


def checkin_shift(vid, date_str, shift):
    validate_volunteer_id(vid)
    validate_date(date_str)
    validate_shift(shift)

    data = load_data()
    if vid not in data["volunteers"]:
        raise ValueError(f"志愿者ID不存在：{vid}")

    date_schedules = data["schedules"].get(date_str, {})
    shift_list = date_schedules.get(shift, [])
    if vid not in shift_list:
        raise ValueError(f"志愿者 {vid} 在 {date_str} {shift} 未排班，无法签到")

    checkin_key = f"{date_str}|{shift}|{vid}"
    if checkin_key in data["checkins"]:
        raise ValueError(f"志愿者 {vid} 在 {date_str} {shift} 已签到")

    data["checkins"][checkin_key] = {
        "volunteer_id": vid,
        "date": date_str,
        "shift": shift,
        "checkin_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_data(data)
    return f"签到成功：{vid} {data['volunteers'][vid]['name']} {date_str} {shift}"


def stats_month(month_str):
    validate_month(month_str)
    data = load_data()

    result = {}
    for vid, vinfo in data["volunteers"].items():
        result[vid] = {
            "name": vinfo["name"],
            "type": vinfo["type"],
            "schedule_count": 0,
            "checkin_count": 0,
        }

    for date_str, date_schedules in data["schedules"].items():
        if not date_str.startswith(month_str):
            continue
        for shift, vids in date_schedules.items():
            for vid in vids:
                if vid in result:
                    result[vid]["schedule_count"] += 1

    for key, cinfo in data["checkins"].items():
        if cinfo["date"].startswith(month_str) and cinfo["volunteer_id"] in result:
            result[cinfo["volunteer_id"]]["checkin_count"] += 1

    return result


def absent_month(month_str):
    validate_month(month_str)
    data = load_data()

    absent_list = []
    for date_str, date_schedules in data["schedules"].items():
        if not date_str.startswith(month_str):
            continue
        for shift, vids in date_schedules.items():
            for vid in vids:
                checkin_key = f"{date_str}|{shift}|{vid}"
                if checkin_key not in data["checkins"]:
                    vinfo = data["volunteers"].get(vid, {})
                    absent_list.append(
                        {
                            "volunteer_id": vid,
                            "name": vinfo.get("name", "未知"),
                            "type": vinfo.get("type", "未知"),
                            "date": date_str,
                            "shift": shift,
                        }
                    )

    absent_list.sort(key=lambda x: (x["date"], x["shift"], x["volunteer_id"]))
    return absent_list
