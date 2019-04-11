from camera.LaneTracking import process_one_frame
import http.client
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import requests

# picar server info
HOST      = '192.168.2.2'
PORT 	  = '8000'

# BASE_URL is variant use to save the format of host and port
BASE_URL = 'http://' + HOST + ':'+ PORT + '/'

def connection_ok():
    """Check whetcher connection is ok

    Post a request to server, if connection ok, server will return http response 'ok'

    Args:
        none

    Returns:
        if connection ok, return True
        if connection not ok, return False

    Raises:
        none
    """
    cmd = 'connection_test'
    url = BASE_URL + cmd
    print('url: %s' % url)
    # if server find there is 'connection_test' in request url, server will response 'Ok'
    try:
        r = requests.get(url)
        if r.text == 'OK':
            return True
    except:
        return False

def __request__(url, times=10):
	for x in range(times):
		try:
			requests.get(url)
			return 0
		except :
			print("Connection error, try again")
	print("Abort")
	return -1

def run_action(cmd):
	"""Ask server to do sth, use in running mode

	Post requests to server, server will do what client want to do according to the url.
	This function for running mode

	Args:
		# ============== Back wheels =============
		'bwready' | 'forward' | 'backward' | 'stop'

		# ============== Front wheels =============
		'fwready' | 'fwleft' | 'fwright' |  'fwstraight'

		# ================ Camera =================
		'camready' | 'camleft' | 'camright' | 'camup' | 'camdown'
	"""
	# set the url include action information
	url = BASE_URL + 'run/?action=' + cmd
	print('url: %s'% url)
	# post request with url
	__request__(url)

def run_speed(speed):
	"""Ask server to set speed, use in running mode

	Post requests to server, server will set speed according to the url.
	This function for running mode.

	Args:
		'0'~'100'
	"""
	# Set set-speed url
	url = BASE_URL + 'run/?speed=' + str(speed)
	print('url: %s'% url)
	# Set speed
	__request__(url)

def QImageToMat(qimg):
    """RGB888"""
    #qimg = QImage()
    #qimg.load("/home/auss/Pictures/test.png")
    qimg = qimg.convertToFormat(QImage.Format_RGB888)
    qimg = qimg.rgbSwapped()
    #assert(qimg.byteCount() == qimg.width() * qimg.height() * 3)

    ptr = qimg.constBits()

    if not ptr:
        return

    ptr.setsize(qimg.byteCount())

    mat = np.array(ptr).reshape( qimg.height(), qimg.width(), 3)  #  Copies the data
    return mat

class QueryImage:
    """Query Image

    Query images form http. eg: queryImage = QueryImage(HOST)

    Attributes:
        host, port. Port default 8080, post need to set when creat a new object

    """

    def __init__(self, host, port=8080, argv="/?action=snapshot"):
        # default port 8080, the same as mjpg-streamer server
        self.host = host
        self.port = port
        self.argv = argv

    def queryImage(self):
        """Query Image

        Query images form http.eg:data = queryImage.queryImage()

        Args:
            None

        Return:
            returnmsg.read(), http response data
        """
        http_data = http.client.HTTPConnection(self.host, self.port)
        http_data.putrequest('GET', self.argv)
        http_data.putheader('Host', self.host)
        http_data.putheader('User-agent', 'python-http.client')
        http_data.putheader('Content-type', 'image/jpeg')
        http_data.endheaders()
        returnmsg = http_data.getresponse()

        return returnmsg.read()


# Make sure there is a connection to the picar server
while True:
    response = connection_ok()
    if response:
        break

# start query image service
queryImage = QueryImage(HOST)

# actuate rear wheels
run_speed(25)
run_action('forward')

while True:

    # Get image from camera
    response = queryImage.queryImage()
    if not response:
        print('no response from querying images')
        continue

    qImage = QImage()
    qImage.loadFromData(response)
    image = QImageToMat(qImage)


    # make copy of raw image
    lane_image = np.copy(image)

    output_image, canny_image, averaged_lines, averaged_line = process_one_frame(image)

    angle = 0
    angle_max = 45
    x_int_mid_min = 50
    m_max_actuate = 15
    x_int_max_actuate = 100
    try:
        print(averaged_lines)
        x1, y1, x2, y2 = averaged_line
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m*x1
        x_int_mid = (image.shape[1]-b)/m - image.shape[1]/2
        print('slope', m)
        print('x-intercept', (image.shape[1]-b)/m)
        print('x-int from middle', x_int_mid)


        if m > 0:
            # go straight if slope is high and x-int is on the right
            if abs(m) > m_max_actuate and x_int_mid > 0:
                print('straight')
                angle = 0
            # turn left if slope is too low or x-int is too left of the image
            else:
                print('turn')
                angle_slope = 0.1 * (m_max_actuate - abs(m)) * angle_max
                angle_x_int = 1 * (x_int_mid_min / max(0.01, x_int_mid)) * angle_max
                angle = max(angle_slope, angle_x_int)
                # print(angle_slope, angle_x_int)
        elif m < 0:
            # go straight if slope is high and x-int is on the right
            if abs(m) > m_max_actuate and x_int_mid < 0:
                print('straight')
                angle = 0
            # turn right if abs(slope) is too low or x-int is too right of the image
            else:
                print('turn')
                angle_slope = 0.1 * (m_max_actuate - abs(m)) * angle_max
                angle_x_int = 1 * (-x_int_mid_min / min(-0.01, x_int_mid)) * angle_max
                angle = max(angle_slope, angle_x_int)
                angle = -angle

    except:
        print('no averaged line')


    # Actuate, angles in the car go from 45 (full left) to 135 (full right)
    angle = angle + 90
    angle = max(min(angle, 135), 45)
    print(angle)
    run_action('fwturn:' + str(angle))

    # show image
    cv2.imshow('result', output_image)
    if cv2.waitKey(100) == 'q':
        continue