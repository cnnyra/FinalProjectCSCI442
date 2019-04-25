# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# pink hsv min: 153, 96,  142
# pink hsv max: 170, 179, 220


def frame_contains_pink_target(frame):
    mask = cv2.inRange(frame, (153, 96, 142), (170, 179, 220))
    width = int(mask.shape[1] * 2/5)
    middle = mask[:, width : mask.shape[1] - width]
    return 255 in middle

def frame_contains_white_border(frame):
    pass

def get_blobs(frame, color):
    #mask = cv2.inRange(frame, (0, 0, 200), (180, 20, 255))
    mask = cv2.inRange(frame, color)
    im2, contours, hierarchy = cv2.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    

def main():
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))

    # allow the camera to warmup
    time.sleep(0.1)

    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        print(frame_contains_pink_target(hsv))
        # show the frame
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
                break

if __name__ == "__main__":
    main()
