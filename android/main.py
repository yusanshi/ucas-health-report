import uiautomator2 as u2
import argparse
import numpy as np
import shutil
import os
import sys
import subprocess
import select

from PIL import Image
from pathlib import Path
from time import sleep
from datetime import date
from config import WST_PASSWORD

parser = argparse.ArgumentParser()
parser.add_argument('--health_code_save_dir',
                    type=str,
                    default=str(Path.home() / "health-code"),
                    help="保存健康码图片的位置")
parser.add_argument('--akm_sample_path',
                    type=str,
                    default=str(Path.home() / "health-code-sample" /
                                "akm.png"),
                    help="示例健康码图片，用于计算相似度")
parser.add_argument('--xck_sample_path',
                    type=str,
                    default=str(Path.home() / "health-code-sample" /
                                "xck.png"),
                    help="示例健康码图片，用于计算相似度")
parser.add_argument('--similiarity_threshold', type=float, default=0.9)
args = parser.parse_args()

Path(args.health_code_save_dir).mkdir(parents=True, exist_ok=True)
akm_path = str(Path(args.health_code_save_dir) / f"{date.today()}-akm.png")
xck_path = str(Path(args.health_code_save_dir) / f"{date.today()}-xck.png")


def get_image_similiarity(first_image_path, second_image_path):
    """Input two images and calculate similarity of them
    """
    first_image = Image.open(first_image_path)
    second_image = Image.open(second_image_path)
    first_image = np.array(first_image).flatten()
    second_image = np.array(second_image).flatten()
    assert first_image.shape == second_image.shape
    return (first_image == second_image).sum() / len(first_image)


def check_image_similarity(current_path, sample_path):
    if Path(sample_path).is_file():
        similiarity = get_image_similiarity(current_path, sample_path)
        print(f'Similiarity: {similiarity}')
        assert similiarity >= args.similiarity_threshold
    else:
        print(
            f'No sample image, save current as sample image to {sample_path}')
        Path(sample_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(current_path, sample_path)
        if input('Is the image OK? [Y/n] ').lower() == 'n':
            os.remove(sample_path)
            print('Sample file removed and exit.')
            sys.exit()


class HealthCodeNotFound(Exception):
    pass


d = u2.connect('localhost:5555')

print('Getting AKM')
d.app_start('com.iflytek.oshall.ahzwfw')
sleep(3)
for _ in range(10):
    sleep(3)
    if d(text='打开系统定位服务').exists:
        assert d(text='取消').exists
        d(text='取消').click()
        continue
    if d(text='安康码').exists and d(text='我的卡包').exists and d(
            text='办事大厅').exists:
        # at home page
        d(text='安康码').click()
        continue
    if d(text='请输入密码').exists:
        # Need to relogin
        d(text='请输入密码').click()
        d.send_keys(WST_PASSWORD)
        d.xpath('@com.iflytek.oshall.ahzwfw:id/login_btn').click()
        continue
    if d(text='切换国康码').exists:
        d.screenshot(akm_path)
        break
else:
    raise HealthCodeNotFound

check_image_similarity(akm_path, args.akm_sample_path)

print('Getting XCK')
d.app_start('com.caict.xingchengka')
sleep(3)
for _ in range(5):
    sleep(3)
    if d.xpath('%的动态行程卡').exists:
        d.screenshot(xck_path)
        break
else:
    raise HealthCodeNotFound

check_image_similarity(xck_path, args.xck_sample_path)

print('Uploading the health codes')
subprocess.run(['bash', 'upload.sh'],
               env={
                   'AKM_PATH': akm_path,
                   'XCK_PATH': xck_path,
               })

d.app_start('com.termux')


class TimeoutExpired(Exception):
    pass


def input_with_timeout(timeout):
    # https://stackoverflow.com/questions/15528939/time-limited-input
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().rstrip('\n')
    raise TimeoutExpired


print(
    'Work done. The device will be shutdown in 10 seconds. Press any key to cancel shutdown: '
)
try:
    input_with_timeout(10)
    print('Shutdown canceled')
except TimeoutExpired:
    subprocess.run('adb -s localhost:5555 shell reboot -p', shell=True)