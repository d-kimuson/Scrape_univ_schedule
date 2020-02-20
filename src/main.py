from chrome_handler import ChromeHandler
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import re
from typing import Tuple, Dict, List, Any, Optional

from settings import LOGIN_URL, USER_NAME, PASSWORD, XPATHS
from gca_handler import GoogleCalnderHandler
from schedules import TERM_TIME_TABLE, Schedule, parse_schedule_text

gca_handler = GoogleCalnderHandler()


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

    def get_schedules_in_this_month(self) -> List[Schedule]:
        table_lines = self.handler.driver \
            .find_element_by_xpath(XPATHS['schedule_table']) \
            .find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')

        schedules: List[Schedule] = []

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

    def get_exist_events(self) -> List[Dict[str, Any]]:
        events = gca_handler.get_events()
        exist_events: List[Dict[str, Any]] = []

        for event in events:
            exist_events.append({
                "title": event['summary'],
                "start_time": GoogleCalnderHandler.time_text_to_datetime(
                    event['start']['dateTime']
                )
            })

        return exist_events

    def update_gca_schedules(self, schedules: List[Schedule]) -> None:
        for schedule in schedules:
            is_duplicate = False
            for event in self.get_exist_events():
                if event['title'] == schedule.title and event['start_time'] == schedule.start_time:
                    is_duplicate = True
                    break

            if not is_duplicate:
                res = gca_handler.add_event(
                    title=schedule.title,
                    start_datetime=schedule.start_time,
                    end_datetime=schedule.end_time,
                    location=schedule.place
                )
                print("{} を作成しました")
            else:
                print("{} は重複しているのでスキップしました.".format(schedule))

    def run(self) -> None:
        try:
            self.login()
            schedules = self.get_schedules_in_this_month()
        finally:
            self.handler.fin()

        self.update_gca_schedules(schedules)


if __name__ == "__main__":
    main = Main(browser=True)
    main.run()
