from datetime import datetime
from typing import Optional
import re

TERM_TIME_TABLE = {
    1: {
        "start": {"hour": 9, "minute": 00},
        "end": {"hour": 9, "minute": 50},
    },
    2: {
        "start": {"hour": 9, "minute": 50},
        "end": {"hour": 10, "minute": 40},
    },
    3: {
        "start": {"hour": 10, "minute": 50},
        "end": {"hour": 11, "minute": 40},
    },
    4: {
        "start": {"hour": 11, "minute": 40},
        "end": {"hour": 12, "minute": 30},
    },
    5: {
        "start": {"hour": 13, "minute": 20},
        "end": {"hour": 14, "minute": 10},
    },
    6: {
        "start": {"hour": 14, "minute": 10},
        "end": {"hour": 15, "minute": 00},
    },
    7: {
        "start": {"hour": 15, "minute": 10},
        "end": {"hour": 16, "minute": 00},
    },
    8: {
        "start": {"hour": 16, "minute": 00},
        "end": {"hour": 16, "minute": 50},
    },
    9: {
        "start": {"hour": 17, "minute": 00},
        "end": {"hour": 17, "minute": 50},
    },
    10: {
        "start": {"hour": 17, "minute": 50},
        "end": {"hour": 18, "minute": 40},
    },
    11: {
        "start": {"hour": 18, "minute": 50},
        "end": {"hour": 19, "minute": 40},
    },
}

one_pattern = re.compile("[1-8]限")
range_pattern = re.compile("[1-8]-[1-8]限")


class Schedule:
    def __init__(self, title: str, start_time: datetime, end_time: datetime, place: Optional[str]) -> None:
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.place = place

    def __repr__(self) -> str:
        return "{}".format(self.title)

    __str__ = __repr__


class UnivClass(Schedule):
    def __init__(self, title: str, start_term: int, year: int,
                 month: int, day: int, end_term: Optional[int],
                 place: Optional[str] = None) -> None:
        self.title = title
        self.place = place
        self.start_term = start_term
        self.end_term = end_term

        if isinstance(end_term, int):
            self.start_time = datetime(
                year,
                month,
                day,
                hour=TERM_TIME_TABLE[start_term]['start']['hour'],
                minute=TERM_TIME_TABLE[start_term]['start']['minute']
            )
            self.end_time = datetime(
                year,
                month,
                day,
                hour=TERM_TIME_TABLE[end_term]['end']['hour'],
                minute=TERM_TIME_TABLE[end_term]['end']['minute']
            )
        else:
            self.start_time = datetime(
                year,
                month,
                day,
                hour=TERM_TIME_TABLE[start_term]['start']['hour'],
                minute=TERM_TIME_TABLE[start_term]['start']['minute']
            )
            self.end_time = datetime(
                year,
                month,
                day,
                hour=TERM_TIME_TABLE[start_term]['end']['hour'],
                minute=TERM_TIME_TABLE[start_term]['end']['minute']
            )

    def __repr__(self) -> str:
        return "{}-{}. {}".format(self.start_term, self.end_term, self.title)

    __str__ = __repr__


def parse_schedule_text(schedule_text: str, date: str) -> Schedule:
    day_match = re.search("\(.*\)", date)
    if isinstance(day_match, re.Match):
        year, month, day = [int(_) for _ in date.replace(
            day_match.group(), ""
        ).split("/")]
    else:
        # 未対応のフォーマット
        raise AttributeError("未対応のフォーマット")

    schedule_text = schedule_text.replace("：", ":")

    if ":" in schedule_text:
        schedule_text = schedule_text.replace(" ", "")
        time_text, place_text, title_text = schedule_text.split(":")

        ranged_match = range_pattern.search(time_text)
        end_term: Optional[str] = None
        if isinstance(ranged_match, re.Match):
            start_term, end_term = ranged_match.group().replace("限", "").split("-")
        else:
            one_match = one_pattern.search(time_text)
            if isinstance(one_match, re.Match):
                start_term = one_match.group().replace("限", "").split("-")[0]
                end_term = None
            else:
                raise AttributeError("未対応のフォーマット")

        return UnivClass(
            title_text,
            int(start_term),
            year,
            month,
            day,
            int(end_term) if isinstance(end_term, str) else None,
            place_text.replace("@", "")
        )
    else:
        raise AttributeError("未対応のフォーマット")
