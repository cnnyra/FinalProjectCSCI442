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

from huntersclient import ClientSocket
import socket
import threading
import queue

import target

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3


IP = '10.200.60.182'
PORT = 5010

robot = maestro.Controller()
body = 6000
headTurn = 6000
headTilt = 6000
motors = 6000
turn = 6000
amount = 400

state = 0
frameCount = 0
scanDir = 0
hasTorqued = False
returnTrip = False
declare = True
orient = True

colors = {
    "pink": ((153, 96, 142),(160, 179, 220)),
    "orange": ((22, 20, 60), (32, 255, 255)),
    "white": ((0, 0, 200), (180, 0, 255))
}
class States:
    startup = 0
    navigation = 1
    mining = 2
    dumping = 3

def scan(frame, *targetColor):
    global scanDir
    up, left = driver.getServoValues()

    targetFound = target.frameContainsTargetColor(frame, *targetColor)
    if targetFound:
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

def turnBody():
    global hasTorqued, state, orient
    up, left = driver.getServoValues()
    if left > 6500:
        driver.goRight(0.1, 1000)
    elif left < 5500:
        driver.goLeft(0.1, 1000)
    if left > 6250:
        hasTorqued = driver.torqueRight(hasTorqued, 725)
    elif left < 5750:
        hasTorqued = driver.torqueLeft(hasTorqued, 725)
    else:
        driver.goLeft(0.01, 0)
        print("Made it to here!")
        orient = True
        return

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
time.sleep(0.5)
#cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

face_cascade = cv2.CascadeClassifier('facefile.xml')

driver.lookUp(0)
# driver.start()
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # State Logic
    if state == States.startup and not orient:
        print("Not Orient")
        
        frameLocated = scan(hsv, *colors["pink"])
        if frameLocated == True:
            turnBody()
    elif state == States.startup and orient:
        #print("Orient")
        driver.lookDown(3000)
        blobs = target.getBlobs(hsv, *colors["orange"])
        for i, blob in enumerate(blobs):
            print("I See blob!!")
            if blobs[i][1] > 450:
                driver.goForward(0.5)
                driver.stop()
                state = States.navigation
                client = ClientSocket(IP, PORT)
                client.sendData("Who put all these rocks here")
                time.sleep(1)
            else:
                driver.goForward(0.1)
    elif state == States.navigation:

        if declare:
            client = ClientSocket(IP, PORT)
            client.sendData("Entering mining area, MINING STATE ACTIVATED")
            print("Entered State: Navigation")
            declare = False
       
        #driver.lookDown(3000)
        xLeft = 280
        xRight = 380
        cXLow = 320
        #targetX = target.getHighestSafePoint(hsv, *colors["white"])
        #print(targetX)
        blobs = target.getBlobs(hsv, *colors["orange"])
        # if targetX < xLeft:
        #     driver.goLeft(0.1, 1000)
        #     #driver.stop()
        # elif targetX > xRight:
        #     driver.goRight(0.1, 1000)
        #     #driver.stop()
        # else:
        #     driver.goForward(0.1)

        driver.goForward(0.1)
        
        for i, blob in enumerate(blobs):
            print("Blob", blob[1])
            if blob[1] > 450:
                driver.goForward(0.5)
                #driver.stop()
                if returnTrip:
                    client = ClientSocket(IP, PORT)
                    client.sendData("Entering dumping area, DUMPING STATE ACTIVATED")
                    state = States.dumping
                    
                else:
                    state = States.mining
                    driver.raiseArm()

                delcare = False
    elif state == States.mining:
        
        if declare:
            client = ClientSocket(IP, PORT)
            client.sendData("Entering mining area, MINING STATE ACTIVATED")
            print("Entered State: Mining")
            declare = False
        #face.findFace(image)
        #if face is not None:

            #client.sendData("Hello human, can I please have the pink ice?")
        #check if color is correct:
        if target.frameContainsTargetColor(hsv, *colors["pink"]):
            pass
            #grab ice
        else:
            client.sendData("Wrong color dumb noob, I said pink")
        returnTrip = True
        state = States.navigation

    elif state == States.dumping:
        print("Entered State: Dumping")
        if target.frameContainsTargetColor(hsv, *colors["pink"]):
            pass
            #drive and face pink box
        #check if box is slightly off center:
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
