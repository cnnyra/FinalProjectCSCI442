import motorDrive as driver
import cv2

class FaceFinder:
    def __init__(centerLeft=280, centerRight=380, centerTop=180, centerBot=300, amount=100):
        self.centerLeft = centerLeft
        self.centerRight = centerRight
        self.centerTop = centerTop
        self.centerBot = centerBot
        self.amount = amount
        self.face_cascade = cv2.CascadeClassifier('facefile.xml')

    def trackHead(x, y):
        ret = False
        if x <= self.centerLeft:
            driver.lookLeft(self.amount)
            ret = True
        elif x >= self.centerRight:
            driver.lookRight(self.amount)
            ret = True

        if y <= self.centerTop:
            driver.lookUp(self.amount)
            ret = True
        elif y >= self.centerBot:
            driver.lookDown(self.amount)
            ret = True

        return ret

    def findFace(frame):
        image = frame.array

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for face in faces:
            ret = trackHead(face[1]+face[3]/2, face[0]+face[2]/2)
