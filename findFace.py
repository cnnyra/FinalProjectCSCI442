import motorDrive as driver
import target
import cv2

class FaceFinder:
    def __init__(self, centerLeft=280, centerRight=380, centerTop=180, centerBot=300, amount=100):
        self.centerLeft = centerLeft
        self.centerRight = centerRight
        self.centerTop = centerTop
        self.centerBot = centerBot
        self.amount = amount
        self.face_cascade = cv2.CascadeClassifier('facefile.xml')

    def trackHead(self, x, y):
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

    def findFace(self, frame):
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        ret = True
        for face in faces:
            ret = self.trackHead(face[0]+face[2]/2, face[1]+face[3]/2)
            if not ret:
                area = face[2]*face[3]
                if area < 1000:
                    driver.goForward(0.5)
                    driver.stop()
        return not ret

