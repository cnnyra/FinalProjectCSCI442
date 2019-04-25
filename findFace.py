import motorDrive as driver
import cv2

# defines the y,x values of the center bounding area
centerLeft = 280
centerRight = 380
centerTop = 180
centerBot = 300

amount = 100


def findFace(y, x):
    ret = False
    if x <= centerLeft:
        driver.lookLeft(amount)
        ret = True
    elif x >= centerRight:
        driver.lookRight(amount)
        ret = True

    if y <= centerTop:
        driver.lookUp(amount)
        ret = True
    elif y >= centerBot:
        driver.lookDown(amount)
        ret = True

    return ret

