from chrome_handler import ChromeHandler
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import re
from typing import Tuple, Dict, List, Any, Optional

from settings import LOGIN_URL, USER_NAME, PASSWORD, XPATHS

one_pattern = re.compile("[1-8]限")
range_pattern = re.compile("[1-8]-[1-8]限")


TERM_TIME_TABLE = {
    "1": {
        "start": {"hour": 9, "minute": 00},
        "end": {"hour": 9, "minute": 50},
    },
    "2": {
        "start": {"hour": 9, "minute": 50},
        "end": {"hour": 10, "minute": 40},
    },
    "3": {
        "start": {"hour": 10, "minute": 50},
        "end": {"hour": 11, "minute": 40},
    },
    "4": {
        "start": {"hour": 11, "minute": 40},
        "end": {"hour": 12, "minute": 30},
    },
    "5": {
        "start": {"hour": 13, "minute": 20},
        "end": {"hour": 14, "minute": 10},
    },
    "6": {
        "start": {"hour": 14, "minute": 10},
        "end": {"hour": 15, "minute": 00},
    },
    "7": {
        "start": {"hour": 15, "minute": 10},
        "end": {"hour": 16, "minute": 00},
    },
    "8": {
        "start": {"hour": 16, "minute": 00},
        "end": {"hour": 16, "minute": 50},
    },
    "9": {
        "start": {"hour": 17, "minute": 00},
        "end": {"hour": 17, "minute": 50},
    },
    "10": {
        "start": {"hour": 17, "minute": 50},
        "end": {"hour": 18, "minute": 40},
    },
    "11": {
        "start": {"hour": 18, "minute": 50},
        "end": {"hour": 19, "minute": 40},
    },
}


def parse_schedule_text(schedule_text: str, date: str) -> Dict[str, Any]:
    day_match = re.search("\(.*\)", date)
    if isinstance(day_match, re.Match):
        year, month, day = [int(_) for _ in date.replace(
            day_match.group(), ""
        ).split("/")]
    else:
        raise AttributeError("未対応のフォーマット")

    schedule_text = schedule_text.replace("：", ":")

    if ":" in schedule_text:
        schedule_text = schedule_text.replace(" ", "")
        time_text, place_text, title_text = schedule_text.split(":")

        ranged_match = range_pattern.search(time_text)
        if isinstance(ranged_match, re.Match):
            start_term, end_term = ranged_match.group().replace("限", "").split("-")
            start_time = datetime(
                year,
                month,
                day,
                hour=TERM_TIME_TABLE[start_term]['start']['hour'],
                minute=TERM_TIME_TABLE[start_term]['start']['minute']
            )
            end_time = datetime(
                year,
                month,
                day,
                hour=TERM_TIME_TABLE[end_term]['end']['hour'],
                minute=TERM_TIME_TABLE[end_term]['end']['minute']
            )
        else:
            one_match = one_pattern.search(time_text)
            if isinstance(one_match, re.Match):
                term = one_match.group().replace("限", "").split("-")[0]

                start_time = datetime(
                    year,
                    month,
                    day,
                    hour=TERM_TIME_TABLE[term]['start']['hour'],
                    minute=TERM_TIME_TABLE[term]['start']['minute']
                )
                end_time = datetime(
                    year,
                    month,
                    day,
                    hour=TERM_TIME_TABLE[term]['end']['hour'],
                    minute=TERM_TIME_TABLE[term]['end']['minute']
                )
            else:
                raise AttributeError("未対応のフォーマット")

        return {
            "start_time": start_time,
            "end_time": end_time,
            "place": place_text.replace("@", ""),
            "title_text": title_text
        }
    elif schedule_text == "":
        return {}
    else:  # 特殊イベント
        return {
            "title_text": schedule_text
        }


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

        schedules = [_.text for _ in schedules_item_list]
        if '登録されている予定はありません' in schedules:
            schedules.remove('登録されている予定はありません')

        return {
            "date": date,
            "schedules": [parse_schedule_text(_, date) for _ in schedules]
        }

    def get_schedules_in_this_month(self) -> List[Dict[str, Any]]:
        table_lines = self.handler.driver \
            .find_element_by_xpath(XPATHS['schedule_table']) \
            .find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')

        schedules: List[Dict[str, Any]] = []

        for table_line in table_lines:
            link_to_each_day = table_line.find_elements_by_class_name('day')

            for link in link_to_each_day:
                try:
                    link.find_element_by_tag_name('a').click()
                except NoSuchElementException:
                    continue

                time.sleep(5)
                schedules.append(self.get_schedule())

        return schedules


if __name__ == "__main__":
    main = Main(browser=True)
    try:
        main.login()
        main.get_schedules_in_this_month()
    finally:
        main.handler.fin()
