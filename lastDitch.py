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
from findFace import FaceFinder

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3


IP = '10.200.27.207'
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
startTime = 0

hasTorqued = False
returnTrip = False
declare = True
orient = False

client = ClientSocket(IP, PORT)
faceFinder = FaceFinder()
colors = {
    "pink": ((153, 96, 142),(160, 179, 220)),
    "orange": ((22, 20, 60), (32, 255, 255)),
    "white": ((0, 0, 200), (180, 0, 255)),
    "ice": ((153, 86, 150
    ),(160, 106, 250))
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
        driver.goLeft(1, 1200)
        driver.stop()
        scanDir = 1 # reset scanStat
    return False

def turnBody():
    global hasTorqued, state, orient
    up, left = driver.getServoValues()
    if left > 6500:
        driver.goRight(0.5, 1000)
        driver.stop()
    elif left < 5500:
        driver.goLeft(0.5, 1000)
        driver.stop()
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
        
        frameLocated = scan(image, *colors["ice"])
        if frameLocated == True:
            turnBody()
    elif state == States.startup and orient:
        print("Orient")
        
        state = States.navigation
        client.sendData("I'm coming for you human")
    elif state == States.navigation:
        driver.goForward(2)
        driver.stop()
        client.sendData("Who put all these gosh didly darn rocks here")
        time.sleep(2)
        driver.goForward(3)
        driver.stop()
        if returnTrip:
            state = States.dumping
            declare = True
            orient = False
            
        else:
            state = States.mining

    elif state == States.mining:
        face = faceFinder.findFace(frame) or face
        
        if declare:
            client.sendData("Entering mining area, MINING STATE ACTIVATED")
            time.sleep(2)
            client.sendData("I would like the pink ice")
            driver.raiseArm()
            driver.openHand()
            time.sleep(2)
            print("Entered State: Mining")
            declare = False
        if face == True:
            
            blobs = target.getBlobs(hsv, *colors["ice"], 25)
            print(blobs)
            if len(blobs) > 0:
                client.sendData("Took you long enough")
                time.sleep(3)
                driver.closeHand()
                driver.goRight(3, 1000)
                driver.stop()
                state = States.navigation
                returnTrip = True
            elif time.time() - startTime > 5:
                startTime = time.time()
                client.sendData("Who taught you colors?")


        
    elif state == States.dumping and not orient:
        if declare:
            client.sendData("Entering dumping area, DUMPING STATE ACTIVATED")
            print("Entered State: Dumping")
            driver.adjustArm()
            driver.lookDown(10000)
            declare = False

        frameLocated = scan(image, *colors["ice"])
        if frameLocated == True:
            turnBody()
    elif state == States.dumping and orient:
        
        driver.goForward(2)
        driver.stop()
        driver.raiseArm()
        driver.centerArm()
        time.sleep(2)
        driver.openHand()            
        client.sendData("Co Bee")
        exit()
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
