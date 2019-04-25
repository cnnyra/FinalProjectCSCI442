import maestro
import time

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3
zeroed = 6000
Tamount = 900
Famount = 800
up = 6000
left = 6000

robot = maestro.Controller()


def start():
    robot.setTarget(4, 6000)
    time.sleep(0.3)
    robot.setTarget(4, 1510)


def torqueRight(torque, amount):
    if not torque:
        robot.setTarget(TURN, 8000)
        time.sleep(0.1)
    robot.setTarget(TURN, zeroed + int(amount))
    return True


def torqueLeft(torque, amount):
    if not torque:
        robot.setTarget(TURN, 8000)
        time.sleep(0.1)
    robot.setTarget(TURN, zeroed - int(amount))
    return True


def goLeft(delay, amount):
    robot.setTarget(TURN, zeroed - int(amount))
    time.sleep(delay)


def goRight(delay, amount):
    robot.setTarget(TURN, zeroed + int(amount))
    time.sleep(delay)


def goForward(delay):
    robot.setTarget(MOTORS, zeroed - Famount)
    time.sleep(delay)


def goBackward(delay):
    robot.setTarget(MOTORS, zeroed + Famount)
    time.sleep(delay)


def lookUp(amount):
    global up
    up += amount
    robot.setTarget(HEADTILT, up)


def lookDown(amount):
    global up
    up -= amount
    robot.setTarget(HEADTILT, up)


def lookRight(amount):
    global left
    left -= amount
    robot.setTarget(HEADTURN, left)


def lookLeft(amount):
    global left
    left += amount
    robot.setTarget(HEADTURN, left)


def stop():
    for i in range(5):
        robot.setTarget(i, 6000)


def getServoValues():
    return up, left
