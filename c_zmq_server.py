import zmq
import sys
from PyQt5.QtCore import QThread, pyqtSignal
import time
import log_utils
log = log_utils.logging_init(__file__)

class ZMQ_Server(QThread):
	signal_recv_message_ret = pyqtSignal(str)
	def __init__(self, port):
		super().__init__()
		self.port = port
		self.ip_port = "tcp://*:" + str(self.port)
		#self.ip_port = "tcp://127.0.0.1:" + str(self.port)
		log.debug("self.ip_port : %s", self.ip_port)
		self.check_time = 1

	def run(self):
		#log.debug("start to run")
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.socket.bind(self.ip_port)
		while True:
			b_message = self.socket.recv()
			#log.debug("Received request: %s", b_message)
			s_message = b_message.decode()
			self.signal_recv_message_ret.emit(s_message)

			#  Do some 'work'
			time.sleep(0.1)

			#  Send reply back to client
			reply = "OK," + str(self.check_time)
			self.socket.send(reply.encode())

	def set_check_time(self, time):
		self.check_time = time
