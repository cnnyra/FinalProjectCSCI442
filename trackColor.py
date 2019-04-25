# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import motorDrive as driver
import findFace as face
from main import scan

import maestro

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

bobo = maestro.Controller()
body = 6000
headTurn = 6000
headTilt = 6000
motors = 6000
turn = 6000
amount = 400

robotLabNight = ((22, 20, 60), (32, 255, 255))
physicsLab = ((10, 63, 100), (25, 255, 255))
clockworkOrange = robotLabNight


def calcWeight(x, y):
    return np.exp(-(480 - y) / 0.01) * x


def calcTurnTime(x):
    return 0.02 * ((x - 320) / 160) ** 2 + 0.25
    # return 0.25


def calcTurnAmount(x):
    return 200 * ((x - 320) / 160) ** 2 + 800


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)
cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

driver.start()
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="driverr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    hsv = cv2.cvtColor(image, cv2.COLOR_driverR2HSV)

    orange = cv2.inRange(hsv, *clockworkOrange)
    orange = cv2.medianBlur(orange, 5)
    # contours, ret = cv2.findContours(orange, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # canny = cv2.Canny(orange, 100, 170)
    contours, ret = cv2.findContours(orange, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # show the frame

    #weightedX = 0
    #weightTotal = 0.01

    move = False
    scan()
    for i in range(len(contours)):
        if cv2.contourArea(contours[i]) > 100:
            move = True
            M = cv2.moments(contours[i])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.drawContours(image, contours, i, (255, 0, 0), thickness=cv2.FILLED)
            cv2.circle(image, (cX, cY), 7, (255, 70, 180), -1)

            #weight = np.exp(-(480 - cY) / 120)
            #weightTotal += weight
            #weightedX += weight * cX
            #framesNoOrange = 0
        # else:
        # framesNoOrange+=1
        # print(framesNoOrange)

    #avgX = weightedX / weightTotal

    # cv2.circle(image, (int(avgX), 320), 17, (255, 70, 180), -1)

    # cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    #if (avgX < 260 and avgX != 0):
     #   driver.goRight(calcTurnTime(avgX), calcTurnAmount(avgX))
      #  driver.stop()
    #elif (avgX > 380 and avgX != 0):
     #   driver.goLeft(calcTurnTime(avgX), calcTurnAmount(avgX))
      #  driver.stop()
    #elif (move):
     #   driver.goForward(0.5)
      #  driver.stop()
    #else:
        # bobo.setTarget(4, 6000)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        driver.stop()
        break
