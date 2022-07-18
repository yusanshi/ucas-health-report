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


class TimeoutExpired(Exception):
    pass


def input_with_timeout(timeout):
    # https://stackoverflow.com/questions/15528939/time-limited-input
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().rstrip('\n')
    raise TimeoutExpired


def wait_for_enter_to_exit(timeout=5):
    """
    Wait for at most `timeout` seconds:
    if user press Enter, exit, else, do nothing.
    """
    try:
        input_with_timeout(timeout)
        sys.exit()
    except TimeoutExpired:
        pass


print('The script will be run in 5 seconds. Press Enter to cancel and exit:')
wait_for_enter_to_exit()

parser = argparse.ArgumentParser()
parser.add_argument('--health_code_dir',
                    type=str,
                    default=str(Path.home() / "health-code"),
                    help="保存健康码图片的位置")
parser.add_argument('--health_code_sample_dir',
                    type=str,
                    default=str(Path.home() / "health-code-sample"),
                    help="示例健康码图片位置，用于计算相似度")
parser.add_argument('--similiarity_threshold', type=float, default=0.8)
args = parser.parse_args()

Path(args.health_code_dir).mkdir(parents=True, exist_ok=True)
xck_path = str(Path(args.health_code_dir) / f"{date.today()}-xck.png")
note_path = str(Path(args.health_code_dir) / f"{date.today()}-note.txt")


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

print('Getting XCK')
d.app_start('com.caict.xingchengka')
sleep(3)
for _ in range(5):
    sleep(3)
    if d.xpath('%的动态行程卡').exists:
        d.screenshot(xck_path)
        check_image_similarity(
            xck_path, str(Path(args.health_code_sample_dir) / "xck.png"))
        break
else:
    raise HealthCodeNotFound

# TODO a tricky solution for shutdown alarms not turning on
d.app_start('com.android.deskclock')
sleep(4)
alarm_switch_xpath = '@com.android.deskclock:id/onoff'
assert len(d.xpath(alarm_switch_xpath).all()) == 1
alarm_switch = d.xpath(alarm_switch_xpath)
alarm_switch.click()
sleep(2)
alarm_switch.click()
sleep(2)
assert alarm_switch.text == 'ON'
sleep(4)

with open(note_path, 'w') as f:
    f.write(f"battery left: {d.device_info['battery']['level']}%")

d.app_start('com.termux')

print('Uploading the health codes')
for _ in range(3):
    try:
        subprocess.run(['bash', 'upload.sh'],
                       check=True,
                       env={
                           'XCK_PATH': xck_path,
                           'NOTE_PATH': note_path,
                       })
        break
    except subprocess.CalledProcessError:
        pass
else:
    raise ValueError('Upload failed')

print(
    'Work done. The device will be shutdown in 5 seconds. Press Enter to cancel shutdown:'
)
wait_for_enter_to_exit()
subprocess.run('adb -s localhost:5555 shell reboot -p', shell=True)
