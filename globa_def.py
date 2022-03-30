import platform

VERSION="20220330_A01"
ZMQ_SERVER_PORT=17688
TAG_OK="OK"
TAG_NG="NG"

TAG_PICO_STATUS="pico_status="
TAG_TERMINUS_STATUS="terminus_status="
TAG_ETH_STATUS="br0_status="
TAG_LCD1602_STATUS="lcd1602_status="
TAG_TEMP_STATUS="temp_status="
TAG_THROTTLED_STATUS="throttled="

broadcast_port = 19999

err_log_filename_prefix = ".ra_err_log_"

FPS_THRESHOLD = 25

"""Media folder"""
if platform.machine() in ('arm', 'arm64', 'aarch64'):
    internal_media_folder = "/home/root/Videos"
else:
    internal_media_folder = "/home/venom/Videos"

udp_sink = "udp://239.11.11.11:15000"
local_sink = "udp://127.0.0.1:15001"

cv2_preview_h264_sink = "udp://127.0.0.1:10011"
hdmi_in_h264_src = "udp://127.0.0.1:10012"
ThumbnailFileFolder = "/.thumbnails/"
