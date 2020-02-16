from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.getcwd()
LOGIN_URL: str = "https://csweb.u-aizu.ac.jp/campusweb/campusportal.do?locale=ja_JP"
CHROME_DRIVER_PATH: str = os.path.join(os.path.expanduser('~'), 'Selenium', 'chromedriver')
USER_NAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('PASSWORD')

XPATHS = {
    "login_button": (
        '/html/body/div[3]/div[2]/table/tbody/'
        'tr[4]/td[3]/div/div[2]/div[2]/div/cen'
        'ter/form/table/tbody/tr[3]/td/button[1]'
    ),
    "schedule_table": (
        '/html/body/div[3]/div[2]/table/tbody/tr[4]'
        '/td[1]/div/div[2]/div[2]/div/div[2]/form/div[3]/table'
    ),
    "date_path": (
        '/html/body/div[3]/div[2]/table/tbody/tr[4]/td[1]/'
        'div/div[2]/div[2]/div/div[2]/form/div[4]/a'
    )
}
