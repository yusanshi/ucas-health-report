import easyocr
import argparse

from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from config import CAS_USERNAME, CAS_PASSWORD

LOGIN_URL = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
UPLOAD_URL = 'https://weixine.ustc.edu.cn/2020/upload/xcm'
APPLY_URL = 'https://weixine.ustc.edu.cn/2020/apply/daliy'

parser = argparse.ArgumentParser()
parser.add_argument('--akm_path', type=str, default='akm.png')
parser.add_argument('--xck_path', type=str, default='xck.png')
args = parser.parse_args()


def main():
    options = Options()
    options.add_argument('--no-sandbox')
    # options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    )

    service = Service('/usr/lib/chromium-browser/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(LOGIN_URL)

    sleep(2)
    WebDriverWait(driver,
                  20).until(EC.presence_of_element_located(
                      (By.ID, 'username')))

    driver.find_element(By.ID, 'username').send_keys(CAS_USERNAME)
    driver.find_element(By.ID, 'password').send_keys(CAS_PASSWORD)
    if driver.find_elements(By.ID, 'validate'):
        # If has the validating code
        image = driver.find_element(By.CSS_SELECTOR,
                                    '.validate img').screenshot_as_png
        reader = easyocr.Reader(['en'])
        captcha = reader.readtext(image, detail=0, allowlist='0123456789')[0]
        print('Captcha recognized: {}'.format(captcha))
        driver.find_element(By.ID, 'validate').send_keys(captcha)

    driver.find_element(By.ID, 'login').click()

    sleep(2)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//a[text()='退出']")))

    driver.get(UPLOAD_URL)
    sleep(2)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//h5[text()='选择14天大数据行程卡：']")))

    xck_form = driver.find_element(By.XPATH,
                                   "//h5[text()='选择14天大数据行程卡：']/parent::div")
    xck_form.find_element(By.TAG_NAME, 'input').send_keys(args.xck_path)
    sleep(2)
    assert '删除' in xck_form.text

    akm_form = driver.find_element(By.XPATH,
                                   "//h5[text()='上传安康码：']/parent::div")
    akm_form.find_element(By.TAG_NAME, 'input').send_keys(args.akm_path)
    sleep(2)
    assert '删除' in akm_form.text

    driver.get(APPLY_URL)
    sleep(2)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//h5[text()='进出校原因：']")))

    driver.find_element(By.XPATH, "//span[text()='前往先研院']").click()
    sleep(1)
    driver.find_element(
        By.XPATH, "//span[text()='我已知悉以上规定并保证按要求执行，做好个人防护，少出行不聚集。']").click()
    sleep(1)
    driver.find_element(By.XPATH, "//button[text()='进出校报备']").click()

    sleep(2)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='提交报备']")))

    driver.find_element(By.XPATH, "//span[text()='先研院']").click()
    sleep(1)
    driver.find_element(By.XPATH,
                        "//input[@name='reason']").send_keys('科研、锻炼身体')
    sleep(1)
    driver.find_element(By.XPATH, "//button[text()='提交报备']").click()

    sleep(2)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//strong[text()='在校可跨校区']")))


if __name__ == '__main__':
    main()
