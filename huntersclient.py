import socket, time
import threading
import queue
import maestro

globalVar = ""


class ClientSocket(threading.Thread):
    def __init__(self, IP, PORT):
        super(ClientSocket, self).__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((IP, PORT))

        print('connected')
        self.alive = threading.Event()
        self.alive.set()

    def recieveData(self):
        global globalVar
        try:
            data = self.s.recv(512)
            print(data)
            globalVar = data
        except IOError as e:
            if e.errno == e.errno.EWOULDBLOCK:
                pass

    def sendData(self, sendingString):
        print('sending')
        sendingString += "\n"
        try:
            print("inside try")
            self.s.send(sendingString.encode('UTF-8'))
        except IOError as e:
            print("well screw you too")
       # print('done sending')

    def run(self):
        global globalVar
        while self.alive.isSet():
            data = self.s.recv(512)
            print(data)
            globalVar = data
            if (data == "0"):
                self.killSocket()

    def killSocket(self):
        self.alive.clear()
        self.s.close()
        print("Goodbye")
        exit()


#IP = '10.200.43.231'
#PORT = 5010
#client = ClientSocket(IP, PORT)
# ##client.start()
#
#for i in ["hello cory", "I've been expecting you", "Are you feeling lucky?"]:
#    time.sleep(1)
#    client.sendData(i)
# print("Exiting Sends")

