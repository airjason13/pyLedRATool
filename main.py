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



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    app = QApplication(sys.argv)
    gui = MainUi()
    qtmodern.styles.dark(app)
    signal.signal(signal.SIGINT, signal_handler)
    # qtmodern.styles.light(app)
    mw = qtmodern.windows.ModernWindow(gui)
    mw.show()
    sys.exit(app.exec_())
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
