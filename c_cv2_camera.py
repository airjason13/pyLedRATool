import cv2
import numpy as np
import time
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QProcess
import os
from globa_def import *


class CV2Camera(QtCore.QThread):
    # 繼承 QtCore.QThread 來建立 Camera 類別
    signal_get_rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray
    signal_cv2_read_fail = QtCore.pyqtSignal()
    signal_tc358743_loopback = QtCore.pyqtSignal()

    def __init__(self, video_src, video_type, parent=None):
        """ 初始化
            - 執行 QtCore.QThread 的初始化
            - 建立 cv2 的 VideoCapture 物件
            - 設定屬性來確認狀態
              - self.connect：連接狀態
              - self.running：讀取狀態
        """
        # 將父類初始化
        super().__init__(parent)
        # self.video_src =  "/dev/video5" # video_src
        self.video_src =  video_src
        self.video_loopback_dst = "/dev/video5"
        self.video_type = video_type
        self.v4l2_loopback_pid = None #ffmpy_utils.v4l2_stream_loopback_with_subprocess(self.video_src, self.video_loopback_dst)
        self.fps_timer = QTimer(self)
        self.fps_timer.timeout.connect(self.fps_counter)
        self.fps_count = 0
        self.fps_timer.start(1000)
        self.fps = 0
        self.s_fps = str(self.fps)
        os.environ['OPENCV_VIDEO_PRIORITY_MSMF'] = '0'
        os.environ['OPENCV_V4L2_CAPTURE_OPTION'] = 'timeout:10'
        # self.no_fps_count = 0
        # 3秒沒有frame後準備重啟
        # self.reopen_threshold = 3


        self.tc358743_connected = False
        self.tc358743_width = 0
        self.tc358743_height = 0
        self.tc358743_fps = 0

        # 建立 cv2 的攝影機物件
        if self.video_type == "v4l2":
            # usb dongle
            self.cam = cv2.VideoCapture(self.video_loopback_dst)
            # 判斷攝影機是否正常連接
            if self.cam is None or not self.cam.isOpened():
                self.connect = False
                self.running = False
            else:
                self.connect = True
                self.running = False
        else:
            # tc358743, do not VideoCapture here
            self.connect = False
            self.running = False
            self.cam = None

    def run(self):
        """ 執行多執行緒
            - 讀取影像
            - 發送影像
            - 簡易異常處理
        """
        log.debug("start to run")
        log.debug("self.video_src = %s", self.video_src)
        # 當正常連接攝影機才能進入迴圈
        while True:
            if self.cam is None:
                if self.connect is False:
                    if self.video_type == "h264":
                        self.cam = cv2.VideoCapture(self.video_loopback_dst)
                    else:
                        log.debug("try to open tc358743")
                        # tc358743, VideoCapture here
                        self.cam = self.open_tc358743_cam()
                time.sleep(1)
                if self.cam is None or not self.cam.isOpened():
                    self.connect = False
                    self.running = False
                else:
                    self.connect = True
                    self.running = True

            if self.running is False:
                log.debug("waiting for start to read")
                # self.signal_cv2_read_fail.emit()
                if self.cam is not None:
                    self.cam.release()
                    self.cam = None
                time.sleep(1)
                continue

            ret, img = self.cam.read()    # 讀取影像
            if ret:
                img = cv2.resize(img, (64, 48))
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # if self.fps_count%30 == 0:
                self.signal_get_rawdata.emit(img)    # 發送影像
                self.fps_count += 1
            else:    # 例外處理
                log.debug("Warning!!!")
                self.connect = False
                self.signal_cv2_read_fail.emit()
                # self.v4l2_loopback_pid.terminate()
                # self.v4l2_loopback_pid = None
                self.cam.release()
                self.cam = None
                continue
                # break

            self.tc358743_connected, self.tc358743_width, self.tc358743_height, self.tc358743_fps \
                = self.get_tc358743_dv_timing()
            if self.tc358743_connected is False:
                self.signal_cv2_read_fail.emit()
                # self.v4l2_loopback_pid.terminate()
                # self.v4l2_loopback_pid = None
                if self.cam is not None:
                    self.cam.release()
                    self.cam = None
                    continue


            '''tmp_connected, tmp_width, tmp_height, tmp_fps = self.get_tc358743_dv_timing()
            if tmp_connected is False or tmp_width != self.tc358743_width or tmp_height != self.tc358743_height or \
                    tmp_fps != self.tc358743_fps:
                log.debug("tmp_connected = %d", tmp_connected)
                log.debug("tmp_width = %d", tmp_width)
                log.debug("tmp_height = %d", tmp_height)
                log.debug("tmp_fps = %d", tmp_fps)
                log.debug("tc358743_width = %d", self.tc358743_width)
                log.debug("tc358743_height = %d", self.tc358743_height)
                log.debug("tc358743_fps = %d", self.tc358743_fps)

                log.debug("need to re-init")
                self.connect = False
                self.v4l2_loopback_pid.terminate()
                self.v4l2_loopback_pid = None
                self.cam.release()
                self.cam = None'''
            #time.sleep(0.005)
        log.debug("stop to run")

    def open(self):
        """ 開啟攝影機影像讀取功能 """
        if self.connect:
            self.running = True    # 啟動讀取狀態

    def stop(self):
        """ 暫停攝影機影像讀取功能 """
        if self.connect:
            self.running = False    # 關閉讀取狀態

    def close(self):
        """ 關閉攝影機功能 """
        if self.connect:
            self.running = False    # 關閉讀取狀態
            time.sleep(1)
            self.cam.release()      # 釋放攝影機

    def get_fps(self):
        log.debug("fps = %d", self.fps)
        return self.fps

    def get_fps_from_loopback_pid(self):
        if self.v4l2_loopback_pid is None:
            return 0
        stdout = self.v4l2_loopback_pid.stdout.readline()
        if stdout is None or stdout == "":
            return 0
        fps = 0
        log.debug("stdout = %s", stdout)
        try: 
            if 'fps=' in stdout:
                list_str = stdout.split(" ")
                i = 0
                d = 0
                for s in list_str:
                    #log.debug("s = %s", s)
                    if 'fps=' in s:
                        d = i
                        # log.debug("d = %d", d)
                        break
                    i += 1
                if i >= len(list_str):
                    fps = 0
                # log.debug("s[d+1] : %s", list_str[d+1])
                fps = int(list_str[d+1])
                # log.debug("fps = %d", fps)
        except:
            log.debug("exception")
        finally:
            pass
        return fps
        
    def fps_counter(self):
        # log.debug("fps_count = %d", self.fps_count)
        # self.fps = self.get_fps_from_loopback_pid()
        self.fps = self.fps_count
        self.fps_count = 0
    
    # useless
    def open_camera(self):
        if self.cam is not None:
            if self.cam.isOpened() is True:
                self.cam.release()
                self.cam = None
        os.system("write_tc358743_edid.sh")
        time.sleep(1)
        self.tc358743_connected, self.tc358743_width, self.tc358743_height, self.tc358743_fps \
            = self.get_tc358743_dv_timing()
        if self.tc358743_connected is True:
            os.system("v4l2-ctl --set-dv-bt-timing query")
            time.sleep(1)
            self.cam = cv2.VideoCapture(self.video_src)

    def setscalesize(self, width, height):
        pass


    def get_tc358743_dv_timing(self):
        # connected = False
        width = 0
        height = 0
        fps = 0
        dv_timings = os.popen("v4l2-ctl --query-dv-timings").read()
        list_dv_timings = dv_timings.split("\n")

        if 'fail' in list_dv_timings[0]:
            # log.debug("not connected")
            connected = False
            return connected, width, height, fps
        else:
            connected = True
        if connected is True:
            for i in list_dv_timings:
                if 'Active width:' in i:
                    width = int(i.split(":")[1])
                if 'Active height:' in i:
                    height = int(i.split(":")[1])
                if 'Pixelclock' in i:
                    fps = int(float(i.split("(")[1].split(" ")[0]))

            #log.debug("width = %d", width)
            #log.debug("height = %d", height)
            #log.debug("fps = %d", fps)
        return connected, width, height, fps

    def open_tc358743_cam(self):
        self.tc358743_connected, self.tc358743_width, self.tc358743_height, self.tc358743_fps \
            = self.get_tc358743_dv_timing()
        if self.tc358743_connected is False:
            return None
        else:
            res_set_dv_bt_timing = os.popen("v4l2-ctl --set-dv-bt-timings query").read()
            log.debug("res_set_dv_bt_timing : %s", res_set_dv_bt_timing)
            ''' with QProcess'''
            #ffmpeg_param = ["ffmpeg", "-hide_banner", "-f", "v4l2", "-i", self.video_src, "-vsync", "2", "-f", "v4l2",
            #              self.video_dst]
            #self.ffmpeg_qprocess.start("ffmpeg", ffmpeg_param)
            self.signal_tc358743_loopback.emit()
            time.sleep(2)
            cam = cv2.VideoCapture(self.video_loopback_dst)

            '''with subprocess'''
            #self.v4l2_loopback_pid = ffmpy_utils.v4l2_stream_loopback_with_subprocess(self.video_src, self.video_loopback_dst)
            #cam = cv2.VideoCapture(self.video_loopback_dst)
            #v4l2_loopback_process = self.v4l2_loopback_pid
            #while True:
            #    stdout = self.v4l2_loopback_pid.stdout.readline()
            #    if stdout is None or stdout == "":
            #        break
            #log.debug("open ok!")
        return cam

    def close_v4l2_loopback_stream(self):
        if self.v4l2_loopback_pid is not None:
            self.v4l2_loopback_pid.terminate()

    def read_ffmpeg_qprocess(self):
        log.debug("ffmpeg_qprocess output: %s", self.ffmpeg_qprocess.readAllStandardOutput())

    def terminate_ffmpeg_qprocess(self):
        log.debug("ffmpeg qprocess terminated")

    def finished_ffmpeg_qprocess(self):
        log.debug("ffmpeg qprocess finished")
