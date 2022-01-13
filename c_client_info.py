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
import datetime
import log_utils
log = log_utils.logging_init(__file__)

class Client_Info_Widget(QWidget):
	def __init__(self, ip, id, parent_widget, **kwargs):
		super(Client_Info_Widget, self).__init__(**kwargs)
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
		self.label_recv_msg.setText("")

		self.label_message_info = ScrollLabel(self.widget)
		self.error_msg_info = ""
		self.total_error_msg_info = ""
		self.total_error_msg_info += self.error_msg_info

		self.label_message_info.setText(self.total_error_msg_info)

		self.widget_client_image = Client_Image()

		#write error log file
		self.error_log_fileuri = os.getcwd() + "/"+ err_log_filename_prefix + self.ip + "_" + \
		                          datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".dat"
		log.debug("self.error_log_fileuri : %s", self.error_log_fileuri)
		self.error_log_file = open(self.error_log_fileuri, 'w')

		#self.pixmap_pico = QPixmap(os.getcwd() + "/image/pico.png")
		#self.label_image_pico = QLabel(self.widget)
		#self.label_image_pico.setPixmap(self.pixmap_pico)
		#self.gridlayout.addWidget(self.label_image_pico, 0, 0)


		self.gridlayout.addWidget(self.label_ip, 0, 0)
		self.gridlayout.addWidget(self.label_id_info, 0, 1)
		self.gridlayout.addWidget(self.label_recv_count, 0, 2)
		self.gridlayout.addWidget(self.label_recv_msg, 1, 0, 1, 3)
		self.gridlayout.addWidget(self.label_message_info, 2, 0, 2, 3)
		self.gridlayout.addWidget(self.widget_client_image, 2, 4)



	def set_error_msg(self, str):
		current_time = "@" +datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "\n"
		str += current_time
		self.error_log_file.write(str)
		self.error_log_file.flush()
		self.error_msg_info = str
		self.total_error_msg_info += self.error_msg_info
		self.label_message_info.setText(self.total_error_msg_info)

	def set_recv_msg(self, recv_msg):
		log.debug("recv_msg:%s", recv_msg)
		if TAG_NG in recv_msg:
			status_list = recv_msg.split(",")
			for status in status_list:
				if TAG_NG in status:
					self.widget_client_image.set_error_tag(status.split("=")[0])
		else:
			status_list = recv_msg.split(",")
			for status in status_list:
				self.widget_client_image.clear_error_tag(status.split("=")[0])
		self.label_recv_msg.setText(recv_msg)
		self.recv_count += 1
		self.label_recv_count.setText("recv_count : " + str(self.recv_count))


class Client_Image(QWidget):
	def __init__(self, *args, **kwargs):
		super(Client_Image, self).__init__(**kwargs)

		self.gridlayout = QGridLayout(self)
		# pico image
		self.pixmap_pico = QPixmap(os.getcwd() + "/image/pico.png")
		self.pixmap_pico.scaledToWidth(96)
		self.pixmap_pico.scaledToHeight(64)
		self.label_image_pico = QLabel(self)
		self.label_image_pico.setScaledContents(True)
		self.label_image_pico.setFixedWidth(48)
		self.label_image_pico.setFixedHeight(64)
		self.label_image_pico.setPixmap(self.pixmap_pico)
		# pi4 image
		self.pixmap_pi4 = QPixmap(os.getcwd() + "/image/pi4.png")
		self.pixmap_pi4.scaledToWidth(96)
		self.pixmap_pi4.scaledToHeight(64)
		self.label_image_pi4 = QLabel(self)
		self.label_image_pi4.setScaledContents(True)
		self.label_image_pi4.setFixedWidth(96)
		self.label_image_pi4.setFixedHeight(64)
		self.label_image_pi4.setPixmap(self.pixmap_pi4)
		# eth hub image
		self.pixmap_eth_hub = QPixmap(os.getcwd() + "/image/eth_hub.png")
		self.pixmap_eth_hub.scaledToWidth(96)
		self.pixmap_eth_hub.scaledToHeight(64)
		self.label_image_eth_hub = QLabel(self)
		self.label_image_eth_hub.setScaledContents(True)
		self.label_image_eth_hub.setFixedWidth(96)
		self.label_image_eth_hub.setFixedHeight(32)
		self.label_image_eth_hub.setPixmap(self.pixmap_eth_hub)

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

		self.gridlayout.addWidget(self.label_image_pico, 1, 1)
		self.gridlayout.addWidget(self.label_image_pi4, 1, 2)
		self.gridlayout.addWidget(self.label_image_eth_hub, 2, 2)
		self.gridlayout.addWidget(self.label_image_lcd1602, 0, 2)
		self.gridlayout.addWidget(self.label_image_eth, 1, 3)

		self.error_part_list = []
		self.show_error = True

	def set_error_tag(self, part):
		log.debug("")
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
			self.label_image_pico.setPixmap(self.pixmap_pico)
			self.label_image_pi4.setPixmap(self.pixmap_pi4)
			self.label_image_eth_hub.setPixmap(self.pixmap_eth_hub)
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
			self.label_image_pico.setPixmap(self.pixmap_pico)
			self.label_image_pi4.setPixmap(self.pixmap_pi4)
			self.label_image_eth_hub.setPixmap(self.pixmap_eth_hub)
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
		#self.label_min_height = self.label.minimumHeight()

		# adding label to the layout
		lay.addWidget(self.label)

	# the setText method
	def setText(self, text):
		# setting text to the label
		self.label.setFont(self._font)
		self.label.setText(text)
		self.label.setMinimumHeight(self.label.minimumHeight() + 100)


