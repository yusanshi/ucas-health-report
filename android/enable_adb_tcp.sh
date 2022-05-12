# https://stackoverflow.com/questions/2604727/how-can-i-connect-to-android-with-adb-over-tcp
setprop service.adb.tcp.port 5555
stop adbd
start adbd
