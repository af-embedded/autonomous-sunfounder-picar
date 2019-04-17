from camera.LaneTracking import process_one_frame, setupToolClasses
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
# run_speed(20)
# run_action('forward')

# Define the codec and create VideoWriter object
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

######### history of m_angle and x_int_mid
num_history = 10
timestep = 20 # ms
history = [[0, 0] for x in range(num_history)]
cum_slope_error = 0 # integrate for I control
cum_x_int_mid_error = 0 # integrate for I control

### Get tools
birdsEye, gradientColorThreshold, curveFitter = setupToolClasses()

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

    binary, color, sobel, skyview = process_one_frame(lane_image, birdsEye, gradientColorThreshold, curveFitter)




    # Show image

    cv2.imshow('result', skyview)
    cv2.imshow('binary', binary)
    cv2.imshow('color', color)
    cv2.imshow('sobel', sobel)
    if cv2.waitKey(timestep) == 27:
        continue

# out.release()
cv2.destroyAllWindows()