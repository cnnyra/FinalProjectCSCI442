# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

# pink hsv min: 153, 96,  142
# pink hsv max: 170, 179, 220


def frameContainsTargetColor(frame, *targetColor):
    mask = cv2.inRange(frame, *targetColor)
    width = int(mask.shape[1] * 2/5)
    middle = mask[:, width : mask.shape[1] - width]
    return 255 in middle

def frameContainsWhiteBorder(frame):
    pass


def getBlobs(frame, *targetColor, minSize=100):
    #mask = cv2.inRange(frame, (0, 0, 200), (180, 20, 255))
    mask = cv2.inRange(frame, *targetColor)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for i, c in enumerate(contours):
        if cv2.contourArea(c) > minSize:
            M = cv2.moments(contours[i])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            rect = cv2.boundingRect(c)
            blobs.append((cX, cY, rect))
    #blobs.sort(key=lambda x: (x[2][1]+x[2][3]), reverse=True)
    return blobs

def getHighestSafePoint(frame, *targetColor):
    mask = cv2.inRange(frame, *targetColor)
    erodeK = np.ones((5,5), np.uint8)
    dilateK = np.ones((7,7), np.uint8) 
    mask = cv2.erode(mask, erodeK, iterations=1)
    mask = cv2.dilate(mask, dilateK, iterations=1)
    mask = cv2.bitwise_not(mask)
    xAvg = 0
    yAvg = 0
    for x in range(len(mask[0])):
        for y in reversed(range(len(mask))):
            yAvg+=1
            if mask[y][x] == 255:
                xAvg += x*(480-y)
                break
    #print(xAvg, yAvg)
    return xAvg/yAvg
            
        
    

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
        print(frameContainsTargetColor(hsv))
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
