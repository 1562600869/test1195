import argparse
import sys

from models import SHIFTS, VOLUNTEER_TYPES
from services import (
    absent_month,
    add_volunteer,
    checkin_shift,
    schedule_shift,
    stats_month,
)


def print_stats(stats):
    if not stats:
        print("暂无志愿者数据")
        return
    headers = ["ID", "姓名", "类型", "排班次数", "到岗次数"]
    widths = [10, 12, 8, 10, 10]
    header_line = "".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * sum(widths))
    for vid in sorted(stats.keys()):
        s = stats[vid]
        row = [
            vid.ljust(widths[0]),
            s["name"].ljust(widths[1]),
            s["type"].ljust(widths[2]),
            str(s["schedule_count"]).ljust(widths[3]),
            str(s["checkin_count"]).ljust(widths[4]),
        ]
        print("".join(row))


def print_absent(absent_list):
    if not absent_list:
        print("该月暂无缺勤记录")
        return
    headers = ["日期", "班次", "ID", "姓名", "类型"]
    widths = [12, 8, 10, 12, 8]
    header_line = "".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * sum(widths))
    for item in absent_list:
        row = [
            item["date"].ljust(widths[0]),
            item["shift"].ljust(widths[1]),
            item["volunteer_id"].ljust(widths[2]),
            item["name"].ljust(widths[3]),
            item["type"].ljust(widths[4]),
        ]
        print("".join(row))


def build_parser():
    parser = argparse.ArgumentParser(
        description="社区消防志愿队值班排班和出勤记录管理工具"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add-volunteer", help="添加志愿者")
    p_add.add_argument("vid", help="志愿者ID")
    p_add.add_argument("name", help="志愿者姓名")
    p_add.add_argument("--phone", required=True, help="电话号码")
    p_add.add_argument(
        "--type",
        required=True,
        choices=VOLUNTEER_TYPES,
        help="志愿者类型：队长/队员/司机/通讯员",
    )

    p_sch = subparsers.add_parser("schedule", help="排班")
    p_sch.add_argument("vid", help="志愿者ID")
    p_sch.add_argument("--date", required=True, help="排班日期 YYYY-MM-DD")
    p_sch.add_argument(
        "--shift", required=True, choices=SHIFTS, help="班次：白班/夜班"
    )

    p_chk = subparsers.add_parser("checkin", help="到岗签到")
    p_chk.add_argument("vid", help="志愿者ID")
    p_chk.add_argument("--date", required=True, help="签到日期 YYYY-MM-DD")
    p_chk.add_argument(
        "--shift", required=True, choices=SHIFTS, help="班次：白班/夜班"
    )

    p_st = subparsers.add_parser("stats", help="统计某月排班与到岗")
    p_st.add_argument("--month", required=True, help="统计月份 YYYY-MM")

    p_ab = subparsers.add_parser("absent", help="查询某月缺勤记录")
    p_ab.add_argument("--month", required=True, help="查询月份 YYYY-MM")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "add-volunteer":
            result = add_volunteer(args.vid, args.name, args.phone, args.type)
            print(result)
        elif args.command == "schedule":
            result = schedule_shift(args.vid, args.date, args.shift)
            print(result)
        elif args.command == "checkin":
            result = checkin_shift(args.vid, args.date, args.shift)
            print(result)
        elif args.command == "stats":
            stats = stats_month(args.month)
            print_stats(stats)
        elif args.command == "absent":
            absent_list = absent_month(args.month)
            print_absent(absent_list)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"系统错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
