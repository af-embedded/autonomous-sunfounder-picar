# Defines the helped to query the image from the car

import http.client
import requests


class CarConnect:
    """Query Image

    Query images form http. eg: queryImage = QueryImage(HOST)

    Attributes:
        host, port. Port default 8080, post need to set when creat a new object

    """

    def __init__(self, host, in_port, out_port):
        # default port 8080, the same as mjpg-streamer server
        self.host = host
        self.in_port = str(in_port)
        self.out_port = str(out_port)
        self.is_connected = False
        self.image = None

    def query_image(self):
        """Query Image

        Query images form http.eg:data = queryImage.queryImage()

        Args:
            None

        Return:
            return_msg.read(), http response data
        """
        try :
            http_data = http.client.HTTPConnection(self.host, self.port)
            http_data.putrequest('GET', "/?action=snapshot")
            http_data.putheader('Host', self.host)
            http_data.putheader('User-agent', 'python-http.client')
            http_data.putheader('Content-type', 'image/jpeg')
            http_data.endheaders()
            return_msg = http_data.getresponse()

            self.image = return_msg.read()
            return True
        except:
            return False

    def request(self, url, times=10):
        for x in range(times):
            try:
                requests.get(url)
                return 0
            except:
                print("Connection error, try again")
        print("Abort")
        return -1

    def run_action(self, cmd):
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
        url = 'http://' + self.host + ':' + self.out_port + '/run/?action=' + cmd
        print('url: %s' % url)
        # post request with url
        self.request(url)

    def run_speed(self, speed):
        """Ask server to set speed, use in running mode

        Post requests to server, server will set speed according to the url.
        This function for running mode.

        Args:
            '0'~'100'
        """
        # Set set-speed url
        url = 'http://' + self.host + ':'+ self.out_port + '/run/?speed=' + str(speed)
        # Set speed
        self.request(url)

    def connection_ok(self):
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
        url = 'http://' + self.host + ':'+ self.outport + '/' + cmd
        print('url: %s' % url)
        # if server find there is 'connection_test' in request url, server will response 'Ok'
        try:
            r = requests.get(url)
            self.is_connected = (r.text == 'OK')
        except:
            self.is_connected = False
        return self.is_connected
