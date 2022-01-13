import os

from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QStyleFactory, QWidget, QHBoxLayout,
                             QVBoxLayout, QFormLayout,
                             QGridLayout, QFrame, QHeaderView, QTableWidgetItem, QMessageBox, QFileDialog,
                             QSlider, QLabel, QLineEdit, QPushButton, QTableWidget, QStackedLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator,
                             QFileDialog, QListWidget, QFileSystemModel, QTreeView, QMenu, QAction, QAbstractItemView,
                             QItemDelegate, QShortcut, QSizePolicy, QRadioButton, QButtonGroup)

from PyQt5.QtGui import QPalette, QColor, QBrush, QFont, QMovie, QPixmap, QPainter, QIcon, QKeySequence, QImage
from PyQt5.QtCore import Qt, QTimer
from c_client_info import *
from c_zmq_server import *
from globa_def import *
import socket
import platform
import fcntl
import struct
import log_utils
log = log_utils.logging_init(__file__)

class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cwd = os.getcwd()
        log.debug("self.cwd = %s", self.cwd)
        self.setWindowTitle('RA Test Tool-- ' + VERSION)

        self.test_ip = []
        self.client_info = []
        self.init_ui()

        self.zmq_server = ZMQ_Server(ZMQ_SERVER_PORT)
        self.zmq_server.signal_recv_message_ret.connect(self.message_parser)
        self.zmq_server.start()
        self.error_check_timer = QTimer(self)
        self.error_check_timer.start(1000)
        self.send_broadcast_timer = QTimer(self)
        self.send_broadcast_timer.timeout.connect(self.send_broadcast)
        self.send_broadcast_timer.start(3000)


    def init_ui(self):
        self.setFixedSize(1600, 800)
        #self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self._font = QFont()
        self._fontScale = 1
        self._font.setPixelSize(24 * self._fontScale)
        self.setFont(self._font)
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.gridlayout = QGridLayout(self.widget)

        self.label_check_period = QLabel(self.widget)
        self.label_check_period.setText("Check Period:")
        self.label_check_period.setFixedWidth(150)
        self.edit_check_period = QLineEdit(self.widget)
        self.edit_check_period.setText("10")
        self.edit_check_period.setFixedWidth(100)
        self.btn_check_period = QPushButton(self.widget)
        self.btn_check_period.setText("Set")
        self.btn_check_period.setFixedWidth(100)
        self.btn_check_period.clicked.connect(self.set_check_period)
        self.gridlayout.addWidget(self.label_check_period, 0, 5)
        self.gridlayout.addWidget(self.edit_check_period, 0, 6)
        self.gridlayout.addWidget(self.btn_check_period, 0, 7)

        # self.pixmap_pico = QPixmap(os.getcwd() + "/image/pico.png")
        # self.label_image_pico = QLabel(self.widget)
        # self.label_image_pico.setPixmap(self.pixmap_pico)
        # self.gridlayout.addWidget(self.label_image_pico, 6, 6)


    def message_parser(self, msg):
        #log.debug("msg = %s", msg)
        str_list = msg.split(",")
        ip = None
        str_error_info = ""
        str_temperature = ""
        for i in range(len(str_list)):
            if str_list[i].startswith("ip="):
                ip = str_list[i].split("=")[1]
                #log.debug("ip : %s", ip)
                if self.add_test_ip_or_not(ip) is True:
                    client_info = Client_Info_Widget(ip, len(self.client_info), self.widget)
                    self.client_info.append(client_info)
                    self.error_check_timer.timeout.connect(self.client_info[len(self.client_info) - 1].widget_client_image.error_alert_timer)

                    self.gridlayout.addWidget(self.client_info[len(self.client_info) - 1], self.client_info[len(self.client_info) - 1].id + 1, 0)
            elif str_list[i].startswith(TAG_PICO_STATUS):
                if str_list[i].split("=")[1] == TAG_NG:
                    str_error_info += "pico error,"
            elif str_list[i].startswith(TAG_TERMINUS_STATUS):
                if str_list[i].split("=")[1] == TAG_NG:
                    str_error_info += "hub error,"
            elif str_list[i].startswith(TAG_ETH_STATUS):
                if str_list[i].split("=")[1] == TAG_NG:
                    str_error_info += "br0 error,"
            elif str_list[i].startswith(TAG_LCD1602_STATUS):
                if str_list[i].split("=")[1] == TAG_NG:
                    str_error_info += "lcd1602 error,"
            elif str_list[i].startswith(TAG_TEMP_STATUS):
                str_temperature = str_list[i].split("=")[1]

        if ip == None:
            log.fatal("ip is None!")
            return

        for i in self.client_info:
            if i.ip == ip:
                if len(str_error_info) > 0:
                    str_error_info += "temp=" + str_temperature # + "\n"
                    log.debug("str_error_info = %s", str_error_info)
                    i.set_error_msg(str_error_info)
                i.set_recv_msg(msg)

    def add_test_ip_or_not(self, recv_ip):
        for i in self.test_ip:
            if recv_ip == i:
                return False
        self.test_ip.append(recv_ip)
        return True

    def get_ip_address(self):
        if platform.machine() in ('arm', 'arm64', 'aarch64'):
            ifname = 'eth0'
        else:
            ifname = 'enp2s0'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15].encode())
            )[20:24])
        except Exception as e:
            # log.error(e)
            ip = ""
        finally:
            return ip

    def send_broadcast(self):
        ip = self.get_ip_address()
        port = broadcast_port
        msg = "ra_server=" + ip + ",port=" + str(ZMQ_SERVER_PORT)
        b_msg = msg.encode()
        if ip != "":
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind((ip, 0))
            sock.sendto(b_msg, ("255.255.255.255", port))
            log.debug("send broadcast ok!")
            sock.close()
        else:
            log.fatal("ip is None")

    def set_check_period(self):
        self.zmq_server.set_check_time(int(self.edit_check_period.text()))