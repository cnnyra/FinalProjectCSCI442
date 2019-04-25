# import the necessary packages
# Arynn Collins and Andrew Johnson
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import motorDrive as driver
import findFace as face
import maestro

#from huntersclient import ClientSocket
import socket
import threading
import queue

import target

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

IP = '10.200.7.125'
PORT = 5010
#client = ClientSocket(IP, PORT)

robot = maestro.Controller()
body = 6000
headTurn = 6000
headTilt = 6000
motors = 6000
turn = 6000
amount = 400

state = 0
frameCount = 0
scanDir = 1
hasTorqued = False
returnTrip = False

def scan():
    global scanDir
    up, left = driver.getServoValues()
    if scanDir == 0:
        driver.lookLeft(100)
        if left >= 8000:
            scanDir = 1
    else:
        driver.lookRight(100)
        if left <= 4000:
            scanDir = 0

def turnBody():
    global hasTorqued, state
    up, left = driver.getServoValues()
    if left > 6500:
        driver.goRight(0.01, 800)
    elif left < 5500:
        driver.goLeft(0.01, 800)
    if left > 6250:
        hasTorqued = driver.torqueRight(hasTorqued, 725)
    elif left < 5750:
        hasTorqued = driver.torqueLeft(hasTorqued, 725)
    else:
        driver.goLeft(0.01, 0)
        state = 1

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
# camera. Ill figure it out
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.5)
#cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

face_cascade = cv2.CascadeClassifier('facefile.xml')


def scan(frame):
    global scanDir
    up, left = driver.getServoValues()

    pink_target_found = target.frame_contains_pink_target(frame)
    if pink_target_found:
        driver.goLeft(0, 0)
        return True
    if scanDir == 0:
        if left >= 8000:
            scanDir = 1
        else:
            driver.lookLeft(100)
    elif scanDir == 1: 
        driver.lookRight(100)
        if left <= 4000:
            scanDir = 0
        elif left == 6100:
            scanDir = 2
    elif scanDir == 2: # not in frame, need to turn wheels
        driver.goLeft(0.1, 1200)
        scanDir = 1 # reset scanStat

    return False 

# driver.start()
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    np_frame = frame.array
    # State Logic
    if state == 0:
        hsv = cv2.cvtColor(np_frame, cv2.COLOR_BGR2HSV)
        frame_located = scan(hsv)

# driver.start()
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="BGR", use_video_port=True):
    image = frame.array
    # State Logic
    if state == 0:
        scan() #scan until endzone marker is found
        turnBody()
        #raise robot's arm and open hand
    elif state == 1:
        #enter obstacle course
        #detect obstacles
        #navigate to endzone marker and avoid obstacles
        # if returnTrip = True:
            # check if blue line is present:
            # if yes, declare "start area"
            # state = 3
        #elif:
            #state = 2
    elif state == 2:
        #check if gold line is present:
            #if yes, declare "mining area"
        #scan for human face
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for face in faces:
            cv2.rectangle(image, (face[0], face[1]), (face[0] + face[2], face[1] + face[3]), (255, 0, 0), 2)
            cv2.circle(image, (int(face[0] + face[2] / 2), int(face[1] + face[3] / 2)), 10, (182, 25, 255))
            ret = face.findFace(face[1] + face[3] / 2, face[0] + face[2] / 2)
            if not ret:
                frameCount += 1
                if frameCount > 20:
                    state = 2
            elif frameCount > 60 and state == 3:
                print(frameCount)
                for i in ["Hello human"]:
                    time.sleep
                    client.sendData(i)
        image = face.getThirds(image)
        #drive to human and ask "can I please have *target color* ice?"
        #check if color is correct:
            #if yes, grab ice
            #if no, declare "wrong color dumb human"
        #returnTrip = True
        #state = 1
    elif state == 3:
        #scan for correct colored box
        #drive to box and face box
        #check if arm is over box:
            #open hand and drop ice into box



    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text

    image = cv2.flip(image, 1)
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        driver.stop()
        break
