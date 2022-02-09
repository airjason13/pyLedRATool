# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from c_mainwindow import MainUi
import sys
from PyQt5.QtWidgets import QApplication
import qtmodern.styles
import qtmodern.windows
import signal
import sys
import os
import time
import globa_def

def signal_handler(signum, frame):
    if signum == signal.SIGINT.value:
        print("QUIT!")
        for i in range(len(gui.server_info)):
            gui.server_info[0].cv2camera.close_v4l2_loopback_stream()
        QApplication.quit()
        sys.exit(1)

def parse_throttled_value( throttled_value):
    res = ""
    if throttled_value & 0x8000 == 0x8000:
        res = res + "Soft temperature limit has occurred,"
    if throttled_value & 0x4000 == 0x4000:
        res = res + "Throttling has occurred,"
    if throttled_value & 0x2000 == 0x2000:
        res = res + "Arm frequency capping has occurred,"
    if throttled_value & 0x1000 == 0x1000:
        res = res + "Arm frequency capping has occurred,"
    if throttled_value & 0x8 == 0x8:
        res = res + "Soft temperature limit active,"
    if throttled_value & 0x4 == 0x4:
        res = res + "Currently throttled,"
    if throttled_value & 0x2 == 0x2:
        res = res + "Arm frequency capped,"
    if throttled_value & 0x1 == 0x1:
        res = res + "Under-voltage detected,"

    return res


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    # res = parse_throttled_value(0xe008)
    # print("res =", res)
    app = QApplication(sys.argv)
    gui = MainUi()
    qtmodern.styles.dark(app)
    signal.signal(signal.SIGINT, signal_handler)
    # qtmodern.styles.light(app)
    mw = qtmodern.windows.ModernWindow(gui)
    mw.show()
    sys.exit(app.exec_())
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
