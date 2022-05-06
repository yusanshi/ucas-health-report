import uiautomator2 as u2
import argparse

from time import sleep
from config import PHONE_NUMBER

parser = argparse.ArgumentParser()
parser.add_argument('--akm_path', type=str, default='akm.png')
parser.add_argument('--xck_path', type=str, default='xck.png')
args = parser.parse_args()

d = u2.connect()

d.app_start('com.iflytek.oshall.ahzwfw')
sleep(2)
assert d(text='安康码').count == 1
d(text='安康码').click()
sleep(2)
if d(text='打开系统定位服务').count > 0:
    assert d(text='取消').count == 1
    d(text='取消').click()
    sleep(2)
assert d(text='切换国康码').count == 1
d.screenshot(args.akm_path)

d.open_url("https://xc.caict.ac.cn/")
sleep(5)
edit_areas = d.xpath("//android.widget.EditText").all()
assert len(edit_areas) == 3
phone_area = edit_areas[0]
captcha_area = edit_areas[1]
checkbox_areas = d.xpath("//android.widget.CheckBox").all()
assert len(checkbox_areas) == 1
checkbox_area = checkbox_areas[0]
button_areas = d.xpath("//android.widget.Button").all()
assert len(button_areas) == 2
get_captcha_area = button_areas[0]
confirm_area = button_areas[1]

phone_area.click()
sleep(1)
d.send_keys(PHONE_NUMBER)
sleep(1)
get_captcha_area.click()
sleep(1)
captcha = input('Please input the captcha: ')
captcha_area.click()
sleep(1)
d.send_keys(captcha)
sleep(1)
checkbox_area.click()
sleep(1)
confirm_area.click()
sleep(2)

assert len(d.xpath('%的动态行程卡').all()) == 1
d.screenshot(args.xck_path)
