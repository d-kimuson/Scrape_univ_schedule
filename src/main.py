from chrome_handler import ChromeHandler
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import re
from typing import Tuple, Dict, List, Any, Optional

from settings import LOGIN_URL, USER_NAME, PASSWORD, XPATHS
from gca_handler import GoogleCalnderHandler

one_pattern = re.compile("[1-8]限")
range_pattern = re.compile("[1-8]-[1-8]限")

gca_handler = GoogleCalnderHandler()


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


class UnivClass:
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


def parse_schedule_text(schedule_text: str, date: str) -> UnivClass:
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


class Main:
    def __init__(self, browser: bool = True) -> None:
        self.handler = ChromeHandler(browser=browser)

    def login(self) -> None:
        self.handler.access(LOGIN_URL, _id='LoginFormSimple')
        self.handler.driver.find_element_by_name(
            'userName'
        ).send_keys(USER_NAME)
        self.handler.driver.find_element_by_name(
            'password'
        ).send_keys(PASSWORD)
        self.handler.driver.find_element_by_name(
            'password'
        ).send_keys(Keys.ENTER)
        self.handler.wait(cl="mysch-portlet")

    def get_schedule(self) -> Dict[str, Any]:
        date = self.handler.driver.find_element_by_xpath(
            XPATHS['date_path']
        ).text
        schedules_item_list = self.handler.driver \
            .find_element_by_class_name("mysch-portlet-list") \
            .find_elements_by_tag_name("li")

        schedule_text_list = [_.text for _ in schedules_item_list]
        if '登録されている予定はありません' in schedule_text_list:
            schedule_text_list.remove('登録されている予定はありません')

        schedules = []
        for schedules_text in schedule_text_list:
            try:
                schedule = parse_schedule_text(schedules_text, date)
            except AttributeError as e:
                print(e)
                continue

            schedules.append(schedule)

        return {
            "date": date,
            "schedules": schedules
        }

    def get_schedules_in_this_month(self) -> List[UnivClass]:
        table_lines = self.handler.driver \
            .find_element_by_xpath(XPATHS['schedule_table']) \
            .find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')

        schedules: List[UnivClass] = []

        for table_line in table_lines:
            link_to_each_day = table_line.find_elements_by_class_name('day')

            for link in link_to_each_day:
                try:
                    link.find_element_by_tag_name('a').click()
                except NoSuchElementException:
                    continue

                time.sleep(5)
                res_get_schedule = self.get_schedule()
                print(res_get_schedule['date'], res_get_schedule['schedules'])

                schedules.extend(res_get_schedule['schedules'])

        return schedules


if __name__ == "__main__":
    main = Main(browser=True)
    try:
        main.login()
        schedules = main.get_schedules_in_this_month()
    finally:
        main.handler.fin()

    for schedule in schedules:
        res = gca_handler.add_event(
            title=schedule.title,
            start_datetime=schedule.start_time,
            end_datetime=schedule.end_time,
            location=schedule.place
        )
        print(res)
