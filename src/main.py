from chrome_handler import ChromeHandler
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from typing import Dict, Any

from settings import LOGIN_URL, USER_NAME, PASSWORD, XPATHS


def parse_schedule_text(schedule_text: str) -> Dict[str, str]:
    if ":" in schedule_text and "：" in schedule_text:
        schedule_text = schedule_text.replace(" ", "")
        time_text, tmp = schedule_text.split(":")
        place_text, title_text = tmp.split("：")

        return {
            "time": time_text,
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
        self.handler.driver.find_element_by_name('userName').send_keys(USER_NAME)
        self.handler.driver.find_element_by_name('password').send_keys(PASSWORD)
        self.handler.driver.find_element_by_name('password').send_keys(Keys.ENTER)
        self.handler.wait(cl="mysch-portlet")

    def get_schedule(self) -> Dict[str, Any]:
        schedules_item_list = self.handler.driver \
            .find_element_by_class_name("mysch-portlet-list") \
            .find_elements_by_tag_name("li")

        schedules = [_.text for _ in schedules_item_list]
        if '登録されている予定はありません' in schedules:
            schedules.remove('登録されている予定はありません')

        return {
            "date": self.handler.driver.find_element_by_xpath(XPATHS['date_path']).text,
            "schedules": [parse_schedule_text(_) for _ in schedules]
        }

    def get_schedules_in_this_month(self) -> None:
        table_lines = self.handler.driver \
            .find_element_by_xpath(XPATHS['schedule_table']) \
            .find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')

        for table_line in table_lines:
            link_to_each_day = table_line.find_elements_by_class_name('day')

            for link in link_to_each_day:
                try:
                    link.find_element_by_tag_name('a').click()
                except NoSuchElementException:
                    continue

                time.sleep(5)
                schedules = self.get_schedule()
                print(schedules)


if __name__ == "__main__":
    main = Main(browser=True)
    try:
        main.login()
        main.get_schedules_in_this_month()
    finally:
        main.handler.fin()
