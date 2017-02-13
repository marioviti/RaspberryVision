with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 10
    #camera.start_preview()
    time.sleep(2)
    stream = io.BytesIO()
    while(True):
        camera.capture_sequence(stream,use_video_port=True)
        data = np.fromstring(stream.getvalue(),dtype=np.uint8)
        #turn the array into a cv2 image
        img = cv2.imdecode(data,1)
