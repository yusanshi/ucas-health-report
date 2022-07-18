# 国科大健康码上传和报备小工具

用于国科大学生自动化上传行程卡、申请出校报备。

## 简介

本项目利用 root 后的安卓物理机获取行程卡并上传到服务器端，利用服务器申请出校报备。安卓手机推荐安装类原生系统（本人用的是 [crDroid](https://crdroid.net/)，它包含安卓 11 和 12 的版本，本人选择的是 11）。

另有使用安卓虚拟机的方案，但是该方法无法正常使用通信行程卡 APP，所以每次需要手动输入验证码，见 [branch `virtual-android`](https://github.com/yusanshi/ucas-health-report/tree/virtual-android)。

由于国科大提交出校报备时还要求当天已经健康打卡，所以请配合 [~~自动打卡工具~~ 开学报到提醒小工具](https://github.com/yusanshi/ucas-health-report) 使用。另记得在健康打卡页面授权系统自动获取京康码和核酸检测报告。

## 免责声明

本脚本所获取的行程卡来自于使用者个人当日的真实数据，不涉及到任何篡改行程卡的行为，因此**原则上**是合规的。但为了避免一些“非原则”的事情发生，本项目作者作如下声明：

1. 仅用于中国科学院大学，其他高校（如中科大）学生请勿使用；
2. 本脚本仅用于辅助使用者减少重复工作量，使用者需对本脚本所做的所有操作负责。

## 开始

### 安卓端

1. 安装通信行程卡 APP，（可选的推荐操作：利用 MagiskHide 之类的工具对它隐藏 root），然后登录好 APP，确保可以正常获得行程卡。

2. 安装 [Termux](https://github.com/termux/termux-app)，按 [[1]](https://wiki.termux.com/wiki/Remote_Access)、[[2]](https://joeprevite.com/ssh-termux-from-computer/) 配置好 SSH server，在电脑上 SSH 进入设备后运行以下命令：

   ```bash
   pkg install android-tools # For adb tools
   pkg install tsu # For sudo
   pkg install python git vim
   pip install wheel IPython

   pkg install libjpeg-turbo # For Pillow installation
   pkg install openblas # For NumPy installation
   pip install Pillow numpy

   pkg install libxml2 libxslt # For uiautomator2 installation
   pip install uiautomator2

   cd ~
   git clone https://github.com/yusanshi/ucas-health-report && cd ucas-health-report && git checkout physical-android

   cd android
   cp upload.sample.sh upload.sh
   vim upload.sh

   sudo bash ./enable_adb_tcp.sh
   adb connect localhost:5555
   # Debuging `main.py`
   ipython
   # After debugging, try running the script directly
   python main.py
   ```

3. 如果手机支持关机闹钟，且手机是备用机因此无需保持开机：

   安装 [Termux:Boot](https://wiki.termux.com/wiki/Termux:Boot)，建立开机启动脚本：
   
   ```bash
   mkdir -p ~/.termux/boot/
   cp ~/ucas-health-report/android/ucas-health-report.sh ~/.termux/boot/
   ```
   设定好每日循环、静音的关机闹钟，本脚本会在闹钟将要唤起、手机开机的时候自动运行，运行结束后自动关机。请注意去掉锁屏密码否则需要手动解锁后才能自动运行脚本。
   
4. 若 3 中的描述与你的使用场景不符，请自行定制化。


### 服务器端

以普通用户身份运行以下命令：

```bash
sudo loginctl enable-linger $USER # 普通用户免登录运行 systemd 服务
/usr/bin/python3 -m pip install selenium easyocr
sudo apt-get install chromium-chromedriver # 非 Ubuntu/Debian 系统自行使用合适的包管理器安装
cd ~
git clone https://github.com/yusanshi/ucas-health-report && cd ucas-health-report && git checkout physical-android

cd server
cp config.sample.py config.py
vim config.py
cp notify.sample.py notify.py
vim notify.py

mkdir -p ~/.config/systemd/user
cp ucas-health-report.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now ucas-health-report.timer
```

> 如果在运行 `systemctl --user daemon-reload` 命令时，显示 `Failed to connect to bus: No such file or directory` 的错误信息，请检查 `echo $XDG_RUNTIME_DIR` 的输出是否为空，如果为空，在 `.bashrc` 中添加 `export XDG_RUNTIME_DIR=/run/user/$(id -u)`，参考[问题](https://serverfault.com/questions/936985/cannot-use-systemctl-user-due-to-failed-to-get-d-bus-connection-permission)。


使用 `/usr/bin/python3 ~/ucas-health-report/server/main.py` 命令来测试健康报备。首次运行需要下载用于 OCR 的模型文件，请耐心等待。如您的下载速度过慢或无法下载，请使用以下命令手动下载：
```bash
wget https://storage.yusanshi.com/easyocr.tar.gz
rm -rfv ~/.EasyOCR
tar -xzvf easyocr.tar.gz -C ~
rm easyocr.tar.gz
```
初步测试成功后，使用 `systemctl --user start ucas-health-report.service` 进一步测试作为 systemd service 时的运行情况。使用 `systemctl --user status ucas-health-report.service` 查看报备日志，使用 `systemctl --user list-timers ucas-health-report.timer`  来查看上次和下次报备时间。

