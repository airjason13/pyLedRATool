import os

from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QStyleFactory, QWidget, QHBoxLayout,
                             QVBoxLayout, QFormLayout,
                             QGridLayout, QFrame, QHeaderView, QTableWidgetItem, QMessageBox, QFileDialog,
                             QSlider, QLabel, QLineEdit, QPushButton, QTableWidget, QStackedLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator,
                             QFileDialog, QListWidget, QFileSystemModel, QTreeView, QMenu, QAction, QAbstractItemView,
                             QItemDelegate, QShortcut, QSizePolicy, QRadioButton, QButtonGroup, QScrollArea)

from PyQt5.QtGui import QPalette, QColor, QBrush, QFont, QMovie, QPixmap, QPainter, QIcon, QKeySequence, QImage
from PyQt5.QtCore import Qt, QTimer, QObject
from globa_def import *
from c_cv2_camera import *
import datetime
import log_utils

log = log_utils.logging_init(__file__)


class Server_Info_Widget(QWidget):
	def __init__(self, ip, id, parent_widget, **kwargs):
		super(Server_Info_Widget, self).__init__(**kwargs)
		self.parent_widget = parent_widget
		self.ip = ip
		self.id = id
		self._font = QFont()
		self._fontScale = 1
		self._font.setPixelSize(18 * self._fontScale)
		self.setFont(self._font)
		self.widget = QWidget(self)
		self.gridlayout = QGridLayout(self.widget)
		self.label_ip = QLabel(self.widget)
		self.label_ip.setText(self.ip)
		self.label_id_info = QLabel(self.widget)
		self.label_id_info.setText("id:" + str(self.id))
		self.label_recv_count = QLabel(self.widget)
		self.recv_count = 0
		self.label_recv_count.setText(str(self.recv_count))
		self.label_recv_msg = QLabel(self.widget)
		self.label_recv_msg.setFixedWidth(900)
		self.label_recv_msg.setText(" ")

		self.label_message_info = ScrollLabel(self.widget)
		self.error_msg_info = ""
		self.total_error_msg_info = ""
		self.total_error_msg_info += self.error_msg_info

		self.label_message_info.setText(self.total_error_msg_info)

		self.widget_server_image = Server_Image()

		self.preview_label = QLabel(self.widget)
		self.pixmap_tiger = QPixmap(os.getcwd() + "/image/tiger.png")
		self.pixmap_tiger.scaledToWidth(96)
		self.pixmap_tiger.scaledToHeight(64)
		self.preview_label.setScaledContents(True)
		self.preview_label.setFixedWidth(128)
		self.preview_label.setFixedHeight(96)
		self.preview_label.setPixmap(self.pixmap_tiger)

		self.ffmpeg_qprocess = None
		# self.run_ffmpeg_loopback()

		self.cv2camera = CV2Camera("/dev/video0", "UYUV")
		self.cv2camera.signal_get_rawdata.connect(self.getRaw)
		self.cv2camera.signal_cv2_read_fail.connect(self.ffmpeg_qprocess_terminate)
		self.cv2camera.signal_tc358743_loopback.connect(self.run_ffmpeg_loopback)

		# write error log file
		self.error_log_file_uri = os.getcwd() + "/" + err_log_filename_prefix + self.ip + "_" + \
		                          datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".dat"
		log.debug("self.error_log_file_uri : %s", self.error_log_file_uri)
		self.error_log_file = open(self.error_log_file_uri, 'w')

		self.gridlayout.addWidget(self.label_ip, 0, 0)
		self.gridlayout.addWidget(self.label_id_info, 0, 1)
		self.gridlayout.addWidget(self.label_recv_count, 0, 2)
		self.gridlayout.addWidget(self.label_recv_msg, 1, 0, 1, 3)
		self.gridlayout.addWidget(self.label_message_info, 2, 0, 2, 3)
		self.gridlayout.addWidget(self.widget_server_image, 2, 4)
		self.gridlayout.addWidget(self.preview_label, 2, 5)

		self.cv2camera.start()

	def set_error_msg(self, str):
		current_time = "@" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "\n"
		str += current_time
		self.error_log_file.write(str)
		self.error_log_file.flush()
		self.error_msg_info = str
		# self.total_error_msg_info += self.error_msg_info
		self.total_error_msg_info = self.error_msg_info
		self.label_message_info.setText(self.total_error_msg_info)

	def set_recv_msg(self, recv_msg):
		# log.debug("recv_msg:%s", recv_msg)
		if TAG_NG in recv_msg:
			status_list = recv_msg.split(",")
			for status in status_list:
				if TAG_NG in status:
					self.widget_server_image.set_error_tag(status.split("=")[0])
		else:
			status_list = recv_msg.split(",")
			for status in status_list:
				self.widget_server_image.clear_error_tag(status.split("=")[0])

		self.label_recv_msg.setText(recv_msg)
		self.recv_count += 1
		self.label_recv_count.setText("recv_count : " + str(self.recv_count))

	def getRaw(self, data):  # data 為接收到的影像
		""" 取得影像 """
		self.showData(data)  # 將影像傳入至 showData()

	def showData(self, img):
		""" 顯示攝影機的影像 """
		self.Ny, self.Nx, _ = img.shape  # 取得影像尺寸

		# 建立 Qimage 物件 (灰階格式)
		# qimg = QtGui.QImage(img[:,:,0].copy().data, self.Nx, self.Ny, QtGui.QImage.Format_Indexed8)

		# 建立 Qimage 物件 (RGB格式)
		qimg = QImage(img.data, self.Nx, self.Ny, QImage.Format_BGR888)

		# viewData 的顯示設定
		# self.preview_label.setScaledContents(True)  # 尺度可變
		### 將 Qimage 物件設置到 viewData 上
		self.preview_label.setPixmap(QPixmap.fromImage(qimg))

	def get_cpu_current_clock(self):
		rep = os.popen("vcgencmd measure_clock arm").read()
		setting_clock = rep.split("=")[1]
		return setting_clock[:7]

	def get_cpu_setting_clock(self):
		rep = os.popen("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq").read()
		current_clock = rep[:len(rep)-1]
		return current_clock

	def get_cv2_fps(self):
		return self.cv2camera.get_fps()

	def run_ffmpeg_loopback(self):
		ffmpeg_param = \
			["-hide_banner", "-f", "v4l2", "-i", "/dev/video0", "-vsync", "2", "-input_format", "RGB3", "-f", "v4l2", "/dev/video5"]
		self.ffmpeg_qprocess = QProcess(self)
		self.ffmpeg_qprocess.setProcessChannelMode(QProcess.MergedChannels)
		self.ffmpeg_qprocess.finished.connect(self.ffmpeg_qprocess_finished)
		self.ffmpeg_qprocess.readyReadStandardOutput.connect(self.ffmpeg_qprocess_stdout)
		os.system("v4l2-ctl --set-dv-bt-timing query")
		time.sleep(1)
		self.ffmpeg_qprocess.start("ffmpeg", ffmpeg_param)

	def ffmpeg_qprocess_finished(self):
		log.debug("ffmpeg_qprocess_finished")

	def ffmpeg_qprocess_stdout(self):
		qprocess_stdout = self.ffmpeg_qprocess.readAllStandardOutput().data().decode().strip()
		log.debug("qprocess_stdout = %s", qprocess_stdout)

	def ffmpeg_qprocess_terminate(self):
		log.debug("")
		self.ffmpeg_qprocess.terminate()
		self.ffmpeg_qprocess = None


class Server_Image(QWidget):
	def __init__(self, *args, **kwargs):
		super(Server_Image, self).__init__(**kwargs)

		self.gridlayout = QGridLayout(self)

		# pi4 image
		self.pixmap_pi4 = QPixmap(os.getcwd() + "/image/pi4.png")
		self.pixmap_pi4.scaledToWidth(96)
		self.pixmap_pi4.scaledToHeight(64)
		self.label_image_pi4 = QLabel(self)
		self.label_image_pi4.setScaledContents(True)
		self.label_image_pi4.setFixedWidth(96)
		self.label_image_pi4.setFixedHeight(64)
		self.label_image_pi4.setPixmap(self.pixmap_pi4)

		# lcd1602 image
		self.pixmap_lcd1602 = QPixmap(os.getcwd() + "/image/lcd1602.png")
		self.pixmap_lcd1602.scaledToWidth(96)
		self.pixmap_lcd1602.scaledToHeight(64)
		self.label_image_lcd1602 = QLabel(self)
		self.label_image_lcd1602.setScaledContents(True)
		self.label_image_lcd1602.setFixedWidth(96)
		self.label_image_lcd1602.setFixedHeight(32)
		self.label_image_lcd1602.setPixmap(self.pixmap_lcd1602)

		# eth image
		self.pixmap_eth = QPixmap(os.getcwd() + "/image/eth.png")
		self.pixmap_eth.scaledToWidth(96)
		self.pixmap_eth.scaledToHeight(64)
		self.label_image_eth = QLabel(self)
		self.label_image_eth.setScaledContents(True)
		self.label_image_eth.setFixedWidth(46)
		self.label_image_eth.setFixedHeight(64)
		self.label_image_eth.setPixmap(self.pixmap_eth)

		self.pixmap_error_red = QPixmap(os.getcwd() + "/image/error_red.png")

		self.gridlayout.addWidget(self.label_image_pi4, 1, 2)
		self.gridlayout.addWidget(self.label_image_lcd1602, 0, 2)
		self.gridlayout.addWidget(self.label_image_eth, 1, 3)

		self.error_part_list = []
		self.show_error = True

	def set_error_tag(self, part):
		# log.debug("")
		for i in self.error_part_list:
			if i == part:
				return
		log.debug("part = %s", part)
		self.error_part_list.append(part)

	def clear_error_tag(self, part):
		if part in self.error_part_list:
			self.error_part_list.remove(part)

	def error_alert_timer(self):
		if len(self.error_part_list) == 0:
			self.label_image_pi4.setPixmap(self.pixmap_pi4)
			self.label_image_eth.setPixmap(self.pixmap_eth)
			self.label_image_lcd1602.setPixmap(self.pixmap_lcd1602)
			return
		if self.show_error is True:
			if "pico_status" in self.error_part_list:
				self.label_image_pico.setPixmap(self.pixmap_error_red)
			if "pi4" in self.error_part_list:
				self.label_image_pi4.setPixmap(self.pixmap_error_red)
			if "terminus_status" in self.error_part_list:
				self.label_image_eth_hub.setPixmap(self.pixmap_error_red)
			if "br0_status" in self.error_part_list:
				self.label_image_eth.setPixmap(self.pixmap_error_red)
			if "lcd1602_status" in self.error_part_list:
				self.label_image_lcd1602.setPixmap(self.pixmap_error_red)
		else:
			self.label_image_pi4.setPixmap(self.pixmap_pi4)
			self.label_image_eth.setPixmap(self.pixmap_eth)
			self.label_image_lcd1602.setPixmap(self.pixmap_lcd1602)

		if self.show_error is True:
			self.show_error = False
		else:
			self.show_error = True


# class for scrollable label
class ScrollLabel(QScrollArea):

	# constructor
	def __init__(self, *args, **kwargs):
		QScrollArea.__init__(self, *args, **kwargs)

		# making widget resizable
		self.setWidgetResizable(True)
		self._font = QFont()
		self._fontScale = 1
		self._font.setPixelSize(18 * self._fontScale)
		self.setFont(self._font)
		# making qwidget object
		content = QWidget(self)
		self.setWidget(content)

		# vertical box layout
		lay = QVBoxLayout(content)

		# creating label
		self.label = QLabel(content)

		# setting alignment to the text
		self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

		# making label multi-line
		self.label.setWordWrap(True)
		self.label.setMinimumWidth(800)
		# self.label_min_height = self.label.minimumHeight()

		# adding label to the layout
		lay.addWidget(self.label)

	# the setText method
	def setText(self, text):
		# setting text to the label
		self.label.setFont(self._font)
		self.label.setText(text)
	# self.label.setMinimumHeight(self.label.minimumHeight() + 100)
