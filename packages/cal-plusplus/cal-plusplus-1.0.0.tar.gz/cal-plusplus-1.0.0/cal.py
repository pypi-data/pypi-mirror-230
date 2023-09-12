import os
import sys
from datetime import date, datetime, timedelta
from unittest import TestCase

import workalendar as workalendar_module
from workalendar.registry import registry

__version__ = "1.0.0"


SUNDAY = 6

ANSI_RESET = "\033[m"
ANSI_REVERSE = "\033[7m"
ANSI_DIMMED = "\033[2m"


def chunks(iterable, chunk_size):
    for i in range(0, int(len(iterable) / chunk_size)):
        yield iterable[i * chunk_size : chunk_size + (i * chunk_size)]


def parse_args(args):
    result = {
        a.split("=")[0]: int(a.split("=")[1])
        if "=" in a and a.split("=")[1].isnumeric()
        else a.split("=")[1]
        if "=" in a
        else True
        for a in args
        if "--" in a
    }
    result["[]"] = [a for a in args if not a.startswith("--")]
    return result


def week_n(first_of_month, week, workalendar=None, week_start=SUNDAY):
    d = first_of_month
    weeks = [[]]

    while d.month == first_of_month.month:
        if d == date.today():
            weeks[-1].append(ANSI_REVERSE + f"{d.day:>2}" + ANSI_RESET)
        elif workalendar and not workalendar.is_working_day(day=d):
            weeks[-1].append(ANSI_DIMMED + f"{d.day:>2}" + ANSI_RESET)
        else:
            weeks[-1].append(f"{d.day:>2}")

        d = d + timedelta(days=1)
        if d.weekday() == SUNDAY:
            weeks.append([])

    # first week should have 7 days
    weeks[0] = ["  " for _ in range(7 - len(weeks[0]))] + weeks[0]
    weeks[-1] = weeks[-1] + ["  " for _ in range(7 - len(weeks[-1]))]

    if len(weeks) > week:
        return weeks[week]
    else:
        return ["  " for _ in range(7)]


def cal(year, *, workalendar=None):
    start_of_months = [date(year, i + 1, 1) for i in range(12)]

    # 2023 - starts on a Sunday
    days = [date(2023, 1, i + 1).strftime("%a") for i in range(7)]

    if workalendar:
        header = f"{year} ({workalendar.name})"
    else:
        header = f"{year}"

    print(f"{header:^61}")

    for row_num, row in enumerate(chunks(start_of_months, 3)):
        # name of month
        print("  ".join([f"{m.strftime('%B'):^20}" for m in row]))

        # days of week
        print(" ".join(["".join([f"{d[:2]:<3}" for d in days]) for _ in row]))

        # weeks of months
        for i in range(6):
            # TODO: only print weeks if one of them has content
            weeks = [week_n(m, i, workalendar) for m in row]

            if any(["".join([d.strip() for d in w]) for w in weeks]):
                print("  ".join([" ".join(w) for w in weeks]))

        # new line separating rows
        if row_num != 3:
            print("")


def cli():
    args = parse_args(sys.argv[1:])

    if "--show-calendars" in args:
        calendars = registry.get_calendars(include_subregions=True)  # This returns a dictionary

        for code, calendar_class in calendars.items():
            print(f"{code}: {calendar_class.name}")

        sys.exit()

    if "--version" in args:
        print(f"cal-plusplus: {__version__}")
        print(f"workalendar: {workalendar_module.__version__}")
        sys.exit()

    if args["[]"] and len(args["[]"]) == 1:
        year = int(args["[]"][0])
    else:
        year = datetime.now().year

    default_cal = os.environ.get("CALPLUSPLUS", "")

    calendar = args.get("--calendar", default_cal)

    try:
        if calendar:
            workalendar = registry.get(calendar)()
        else:
            workalendar = None
    except TypeError:
        print(f"{calendar} doesn't appear to be a valid calendar in workalendar")
        print("")
        print("Use --show-calendars to list valid calendars")
        sys.exit(1)

    cal(year, workalendar=workalendar)


if __name__ == "__main__":
    cli()


class TestCal(TestCase):
    def test_week_n(self):
        week = week_n(date(2023, 1, 1), 2)
        self.assertEqual(week, ["15", "16", "17", "18", "19", "20", "21"])
