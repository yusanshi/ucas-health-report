import argparse
import easyocr
import random
import sys

from pathlib import Path
from time import sleep
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

try:
    from notify import notify
except ModuleNotFoundError:

    def notify(message, attachment_path=None):
        pass


from config import CAS_USERNAME, CAS_PASSWORD

LOGIN_URL = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
APPLY_URL = 'https://weixine.ustc.edu.cn/2020/apply/daliy'


def main():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    )

    service = Service('/usr/lib/chromium-browser/chromedriver')
    with webdriver.Chrome(service=service, options=options) as driver:
        driver.get(LOGIN_URL)

        sleep(2)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'username')))

        driver.find_element(By.ID, 'username').send_keys(CAS_USERNAME)
        driver.find_element(By.ID, 'password').send_keys(CAS_PASSWORD)
        if driver.find_elements(By.ID, 'validate'):
            # If has the validating code
            image = driver.find_element(By.CSS_SELECTOR,
                                        '.validate img').screenshot_as_png
            reader = easyocr.Reader(['en'])
            captcha = reader.readtext(image, detail=0,
                                      allowlist='0123456789')[0]
            print('Captcha recognized: {}'.format(captcha))
            driver.find_element(By.ID, 'validate').send_keys(captcha)

        driver.find_element(By.ID, 'login').click()

        sleep(2)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='退出']")))

        driver.get(APPLY_URL)
        sleep(2)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h5[text()='进出校原因：']")))

        driver.find_element(By.XPATH, "//span[text()='前往先研院']").click()
        sleep(1)
        driver.find_element(
            By.XPATH,
            "//span[text()='我已知悉学校防疫规定并保证按要求执行，做好个人防护，少出行不聚集。']").click()
        sleep(1)
        driver.find_element(By.XPATH, "//button[text()='进出校报备']").click()

        sleep(2)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[text()='提交报备']")))

        driver.find_element(By.XPATH, "//span[text()='先研院']").click()

        sleep(1)
        Select(driver.find_element(By.ID, "reason")).select_by_value('其它事宜')
        reasons = ['科研、锻炼身体', '跑步', '锻炼身体']
        driver.find_element(By.ID, "comment").send_keys(random.choice(reasons))

        sleep(1)
        driver.find_element(By.XPATH, "//button[text()='提交报备']").click()

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//p[contains(text(),'报备成功，门禁权限将在稍后生效')]")))


if __name__ == '__main__':
    errors = []
    for i in range(5):
        try:
            main()
            message = '[UCAS Health Report] Success'
            print(message)
            notify(message)
            break
        except Exception as e:
            print(f'Failed for {i+1} times: {e}')
            errors.append(str(e))
            sleep(300 * (i + 1))
    else:
        notify('[UCAS Health Report] Failed: ' + str(list(enumerate(errors))))
