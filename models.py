import re
from datetime import datetime

VOLUNTEER_TYPES = ("队长", "队员", "司机", "通讯员")
SHIFTS = ("白班", "夜班")
MAX_PER_SHIFT = 5

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
MONTH_PATTERN = r"^\d{4}-\d{2}$"


def validate_volunteer_type(vtype):
    if vtype not in VOLUNTEER_TYPES:
        raise ValueError(
            f"志愿者类型无效：{vtype}，必须是以下之一：{', '.join(VOLUNTEER_TYPES)}"
        )


def validate_shift(shift):
    if shift not in SHIFTS:
        raise ValueError(
            f"班次无效：{shift}，必须是以下之一：{', '.join(SHIFTS)}"
        )


def validate_date(date_str):
    if not re.match(DATE_PATTERN, date_str):
        raise ValueError(f"日期格式无效：{date_str}，请使用 YYYY-MM-DD 格式")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日期不存在：{date_str}")


def validate_month(month_str):
    if not re.match(MONTH_PATTERN, month_str):
        raise ValueError(f"月份格式无效：{month_str}，请使用 YYYY-MM 格式")
    try:
        datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        raise ValueError(f"月份不存在：{month_str}")


def validate_phone(phone):
    if not phone:
        raise ValueError("电话号码不能为空")


def validate_volunteer_id(vid):
    if not vid or not vid.strip():
        raise ValueError("志愿者ID不能为空")
