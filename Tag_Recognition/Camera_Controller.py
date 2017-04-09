import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray
import threading
import cv2
import time
import settings


"""
# import the necessary packages
from picamera.array import PiRGBArray
from picamera.array import PiYUVArray
from picamera import PiCamera
import time
import cv2
import io
import socket

camera_log = { 'awb_gains' : [] }

def reset_camera_values(camera):
	# release fixed mode
	camera.exposure_mode = "auto"
	camera.awb_mode = "auto"
	# wait for sensors to settle
	time.sleep(0.5)
	# make new readings
	gain = camera.awb_gains
	# reset fixed mode
	camera.exposure_mode = "off"
	camera.awb_mode = "off"
	camera.awb_gains = gain
	# save in log
	global camera_log
	camera_log['awb_gains'] += [gain]

def initialize_camera(resolution,framerate,fixed=True):
	camera = PiCamera()
	camera.resolution = resolution
	camera.framerate = framerate
	# Wait for the camera gain sensor to set
	time.sleep(2)
	if fixed:
		# Now set fixed values
		camera.shutter_speed = camera.exposure_speed
		camera.exposure_mode = "off"
		gain = camera.awb_gains
		camera.awb_mode = "off"
		# now gain is set
		camera.awb_gains = gain
		# save in log
		global camera_log
		camera_log['awb_gains'] += [gain]
	return camera

def show_video(resolution=(640, 480),framerate=10,fixed=True,quit_key='q'):

	# initialize the camera
	camera=initialize_camera(resolution,framerate,fixed=fixed)

	# initialize buffer to hold frame
	stream = PiRGBArray(camera, size=resolution)

	# capture frames from the camera
	while(True):
		camera.capture(stream, format='bgr', use_video_port=True)
		image = stream.array

		# show the frame
		cv2.imshow("Frame", image)
		key = cv2.waitKey(1) & 0xFF

		# clear the stream in preparation for the next frame
		stream.truncate(0)

		# if the `quit_key` key was pressed, break from the loop
		if key == ord(quit_key):
			break

# for the server: nc -l 8000 | vlc --demux h264 -
def stream_video(server_addr,port=8000,resolution=(640, 480),framerate=10,fixed=True):

	# Connect a client socket to my_server:8000 (change my_server to the
	# hostname of your server)
	client_socket = socket.socket()
	client_socket.connect((server_addr, port))

	# Make a file-like object out of the connection
	connection = client_socket.makefile('wb')
	try:
		# initialize the camera
		camera=initialize_camera(resolution,framerate,fixed=fixed)
		camera.start_recording(connection, format='h264')
		camera.wait_recording(60)
		camera.stop_recording()
	finally:
		connection.close()
		client_socket.close()

"""


class Camera_Controller(threading.Thread):
    def __init__(self, camera_settings = settings.camera_settings):
        super(Camera_Controller, self).__init__()
        # load camera settings
        self.load_camera_settings(camera_settings)
        # initialize camera
        self.initialize_camera()
        # initialize image buffer
        self.initialize_image_buffer()
        # initialize lock
        self.initialize_locks()

    def shutdown(self):
        self.running = False

    def initialize_locks(self):
        self.processing_buffer_lock = threading.Lock()

    def load_camera_settings(self,camera_settings):
        self.aexposure = camera_settings['aexposure']
        self.awb = camera_settings['awb']
        self.awb_gains = camera_settings['awb_gains']
        self.resolution = camera_settings['resolution']
        self.framerate = camera_settings['framerate']
        self.frame_format = camera_settings['frame']['format']
        self.use_video_port = camera_settings['frame']['use_video_port']

    def initialize_camera(self):
        self.camera = PiCamera()
        # wait for camera to heat up sensors
        time.sleep(2)
        if not self.awb:
            # default on
            self.camera.awb_mode = "off"
            self.camera.awb_gains = self.awb_gains
        if not self.aexposure:
            # default on
            self.camera.exposure_mode = "off"
        self.camera.resolution = self.resolution
        self.camera.framerate = self.framerate

    def initialize_image_buffer(self):
        self.image_buffer = PiRGBArray(self.camera)
        self.processing_buffer = None

    def run(self):
        # setting flag for gracious termination
        self.running = True
        for frame in self.camera.capture_continuous(self.image_buffer, \
            format=self.frame_format , use_video_port=self.use_video_port):
            if not self.running:
                break
            with self.processing_buffer_lock:
                #print "captured image"
                self.processing_buffer = frame.array.copy() # keep a copy
            self.image_buffer.seek(0)
            self.image_buffer.truncate()
