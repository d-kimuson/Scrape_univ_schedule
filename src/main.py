from chrome_handler import ChromeHandler
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
import time
import re
from typing import Tuple, Dict, List, Any, Optional

from settings import LOGIN_URL, USER_NAME, PASSWORD, XPATHS
from gca_handler import GoogleCalnderHandler
from schedules import TERM_TIME_TABLE, Schedule, parse_schedule_text

# On Click後のLoading待ち時間
# 良い対処が思いつかないので, とりあえず固定時間待つ
# 回線やJSの実行速度に左右されるので, 適切に設定して走らせる
MAX_WAIT_LOAD_TIME = 20

gca_handler = GoogleCalnderHandler()


class Main:
    def __init__(self, browser: bool = False) -> None:
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

    def wait_until_loading(self) -> None:
        loading_element = self.handler.driver.find_element_by_id("wf_PTW0005100-s_20120920145137-mysch-portlet-list-loading")

        for _ in range(MAX_WAIT_LOAD_TIME):
            """
            1. click day
            2. loading_element が 表示される
            3. loading_element が display=None に

            1秒毎にチェックして, ローディング終了まで実行を待つ
            """
            if not loading_element.is_displayed():
                return None

            time.sleep(1)

    def get_schedule_from_element(self, element: WebElement) -> Optional[Dict[str, Any]]:
        try:
            element.find_element_by_tag_name('a').click()
        except NoSuchElementException:
            return None
        finally:
            self.wait_until_loading()

        schedule = self.get_schedule()
        print(schedule['date'], schedule['schedules'])

        return schedule

    def get_schedules_in_this_month(self) -> List[Schedule]:
        # 今月のカレンダーから予定を取り出す
        table_lines = self.handler.driver \
            .find_element_by_xpath(XPATHS['schedule_table']) \
            .find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')

        schedules: List[Schedule] = []

        # 週に対するループ
        for table_line in table_lines:
            link_to_each_day = table_line.find_elements_by_class_name('day')
            _ = table_line.find_elements_by_class_name('today')

            if len(_) != 0:
                link_to_each_day.append(_[0])

            # 日付に対するループ
            for link in link_to_each_day:
                # ある日付の予定リストを取得し, schedules に書き出す
                schedule = self.get_schedule_from_element(link)
                if isinstance(schedule, dict):
                    schedules.extend(schedule['schedules'])

        return schedules

    def get_exist_events(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        events = gca_handler.get_events(*args, **kwargs)
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
        """
        Schedule で Google Calender を上書きするメソッド
        """
        for schedule in schedules:
            # 重複判定処理
            # タイトルと, 開始時刻が同一のイベントが存在するときはスキップする

            is_duplicate = False
            for event in self.get_exist_events(max_result_num=100):
                if event['title'].replace(" ", "") == schedule.title.replace(" ", "") and event['start_time'] == schedule.start_time:
                    is_duplicate = True
                    break

            if not is_duplicate:
                res = gca_handler.add_event(
                    title=schedule.title,
                    start_datetime=schedule.start_time,
                    end_datetime=schedule.end_time,
                    location=schedule.place
                )
                print("{} を作成しました".format(schedule))
            else:
                print("{} は重複しているのでスキップしました.".format(schedule))

    def reset_month_schedules(self, year: int, month: int) -> None:
        events = self.handler.driver.get_events(year=year, month=month)

        for event in events:
            event_year, event_month, _ = event['start']['dateTime'].split('-')
            if int(event_year) == year and int(event_month) == month:
                self.handler.driver.delete_event(event['id'])
            else:
                # 次月のスケジュール => 終了
                break

    def run(self) -> None:
        # 起点メソッド
        try:
            self.login()
            schedules = self.get_schedules_in_this_month()
        finally:
            # Chronium を終了する
            self.handler.fin()

        # 全ての今月の予定が入った schedules を Google Calender に追加
        self.update_gca_schedules(schedules)


if __name__ == "__main__":
    main = Main(browser=False)
    main.run()
