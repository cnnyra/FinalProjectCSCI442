# import the necessary packages
# Arynn Collins and Andrew Johnson
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import BoboGo as bg
# import BoboFace as bf
import BoboFollow as bf
import maestro

from huntersclient import ClientSocket
import socket, time
import threading
import queue

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

IP = '10.200.7.125'
PORT = 5010
client = ClientSocket(IP, PORT)

bobo = maestro.Controller()
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
cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

face_cascade = cv2.CascadeClassifier('facefile.xml')


def scan():
    global scanDir
    up, left = bg.getServoValues()
    print("Titties      " + str(up) + ", " + str(left))
    if scanDir == 0:
        bg.lookLeft(100)
        if left >= 8000:
            scanDir = 1
    else:
        bg.lookRight(100)
        if left <= 4000:
            scanDir = 0


# bg.start()
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # State Logic
    if state == 0:
        scan()
    elif state == 2:
        up, left = bg.getServoValues()
        if left > 6500:
            bg.goRight(0.01, 800)
        elif left < 5500:
            bg.goLeft(0.01, 800)
        if left > 6250:
            hasTorqued = bg.torqueRight(hasTorqued, 725)
        elif left < 5750:
            hasTorqued = bg.torqueLeft(hasTorqued, 725)
        else:
            bg.goLeft(0.01, 0)
            frameCount = 0
            state = 3

    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if state == 0 and faces is not None: state = 1

    for face in faces:
        cv2.rectangle(image, (face[0], face[1]), (face[0] + face[2], face[1] + face[3]), (255, 0, 0), 2)
        cv2.circle(image, (int(face[0] + face[2] / 2), int(face[1] + face[3] / 2)), 10, (182, 25, 255))
        ret = bf.findFace(face[1] + face[3] / 2, face[0] + face[2] / 2)
        if not ret:
            frameCount += 1
            if frameCount > 30 and state == 1:
                state = 2
        elif frameCount > 60 and state == 3:
            print(frameCount)
            for i in ["Hello human"]:
                time.sleep
                client.sendData(i)
        state = 0

    image = bf.getThirds(image)
    image = cv2.flip(image, 1)
    cv2.imshow("Frame", image)

    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        bg.stop()
        break