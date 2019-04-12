from camera.LaneTracking import process_one_frame
import http.client
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import requests
import math

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
run_speed(19)
run_action('forward')

# Define the codec and create VideoWriter object
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

# Get images and calculate steering angle
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

    # write to video writer
    # out.write(lane_image)

    output_image, canny_image, averaged_lines, averaged_line = process_one_frame(image)

    angle = 0
    angle_max = 45
    x_int_mid_min = 50
    image_mid_offset = 100
    x_int_max_actuate = 200
    correction_angle = 5
    steering_coeff = 0.3
    slope_angle_bias = -5

    try:
        print(averaged_lines)
        x1, y1, x2, y2 = averaged_line
        m = (y2 - y1) / (x2 - x1)
        m_angle = math.degrees(math.atan(1/m)) + slope_angle_bias # left is positive
        b = y1 - m*x1
        x_int_mid = (image.shape[1]-b)/m - (image.shape[1]/2 + image_mid_offset)
        print('slope', m, str(m_angle) + 'deg')
        print('x-int from middle', x_int_mid)

        if m_angle > 0:
            # go right if x-int is too far right
            if x_int_mid > x_int_max_actuate:
                print('turn right - x-int too far right')
                angle = correction_angle

            # turn left
            else:
                print('turn left')
                angle = -steering_coeff*m_angle
        elif m_angle < 0:
            # go left if x-int is on the left
            if x_int_mid < -x_int_max_actuate:
                print('turn left - x-int too far left')
                angle = -correction_angle
            # turn right
            else:
                print('turn right')
                angle = -steering_coeff*m_angle
        else:
            print('straight')
            angle = 0

    except:
        print('no averaged line')
        run_action('stop')
        break


    # Actuate, angles in the car go from 45 (full left) to 135 (full right)
    print(angle)
    angle = angle + 90
    angle = max(min(angle, 135), 45)
    run_action('fwturn:' + str(angle))

    # show image
    cv2.imshow('result', output_image)
    if cv2.waitKey(20) == 27:
        continue

# out.release()
cv2.destroyAllWindows()