#!/data/data/com.termux/files/usr/bin/sh

termux-wake-lock
sudo bash ~/ucas-health-report/android/enable_adb_tcp.sh
adb connect localhost:5555

# Run in foreground
adb -s localhost:5555 shell am start -n com.termux/.app.TermuxActivity
sleep 10 # Wait for network
adb -s localhost:5555 shell input text "cd\ ~/ucas-health-report/android\ \&\&\ python\ main.py"
adb -s localhost:5555 shell input keyevent "KEYCODE_ENTER"
