from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

from settings import CHROME_DRIVER_PATH


class ChromeHandler:
    def __init__(self, browser: bool = False) -> None:
        op = Options()
        op.add_argument("--disable-gpu")
        op.add_argument("--disable-extensions")
        op.add_argument("--proxy-server='direct://'")
        op.add_argument("--proxy-bypass-list=*")
        op.add_argument("--start-maximized")
        op.add_argument("--headless")

        if browser:
            self.driver = webdriver.Chrome(
                CHROME_DRIVER_PATH)
        else:
            self.driver = webdriver.Chrome(
                CHROME_DRIVER_PATH, options=op
            )

        self.soup = None

    def __wait__(self, _time, key, val=None):
        try:
            WebDriverWait(self.driver, _time).until(
                EC.presence_of_element_located(
                    (key, val)
                )
            )
        except Exception as e:
            print(e)

    def wait(self, _id=None, cl=None, selector=None, _time=30):
        if _id is None and cl is None:
            self.__wait__(_time, key='all')
        else:
            params = [
                (_id, By.ID),
                (cl, By.CLASS_NAME),
                (selector, By.CSS_SELECTOR)
            ]
            for _set in params:
                if _set[0] is not None:
                    self.__wait__(
                        _time, _set[1], _set[0]
                    )

    def access(self, url, _id=None, cl=None, selector=None):
        self.driver.get(url)
        self.wait(_id=_id, cl=cl, selector=selector)
        self.set_soup()

    def set_soup(self):
        self.soup = BeautifulSoup(
            self.driver.page_source,
            features="html.parser"
        )

    def fin(self):
        self.driver.quit()
