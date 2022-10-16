from base import *

from .StatusData.statusData import StatusData

class Client:

    def __init__(self):

        self.ip = None
        self.port = None

        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #main socket, all data transportation will be handled through this object

        self.branch = "PRE_CONNECTION"
        self.status = "WAITING_FOR_INPUT"
        #both are used for process diversion and tracking, the branch being more general

        self.StatusData = StatusData()
        #everything related to the process, starting from taking the keyboard input to displaying
        #the server output will be stored here

        self.hstname = socket.gethostname()
        #IP address of the device this script or program is executed on,
        #can be used for fast checking the app on the same device the server is running

        print("The IP of this device:" + str(socket.gethostbyname(self.hstname)))
        #if you want to check both programs on the same computer, compy paste this IP
        #from associated message when print on the console

    def run(self):

        while True:

            if self.branch == "CONNECTED":

                if self.StatusData.status == "WAITING_FOR_INPUT":

                    tempInput = input()

                    if tempInput == "close":
                        break

                    tempInputList = tempInput.split(" ")

                    tempInput = ""

                    count = 0

                    for component in tempInputList:

                        tempInput += component

                        if count < 1:

                            tempInput += "!"

                            count += 1

                        else:

                            if component != tempInputList[-1]:

                                tempInput += " "

                    #above algorithm is used for formatting the input in a suitable
                    #string adhering to our, pre-determined protocol the server would understand

                    mtbse = tempInput.encode("utf-8")  # str.encode(mtbs)
                    #encoding entered string into an utf-8 binary format that unlike the name suggests,
                    #in most cases is comprising of more than 8 bytes and can map lots of characters
                    #not being represented is ASCII, like the ones found in Turkish, Chinese and Russian languages

                    mtbs = "bufferSize " + str(len(mtbse))
                    #this string will be sent before the origininal message,
                    #it carries the size of the encoded message we have entered
                    #so the server shall know how many bytes to expect

                    for i in range(0,20):

                        if i >= len(mtbs):

                            mtbs += " "

                    #filling the size message to 20 bytes,
                    #this is necessary, since the server waiting for byte size of a message
                    #will always be waiting for 20 bytes

                    mtbsee = mtbs.encode("utf-8")#str.encode(mtbs)
                    #encoding the size message, it will not contain non ascii characters
                    #but needed since sockets in python can only send messages of type byte

                    self.socket.send(mtbsee)

                    self.StatusData.receivedBytes = 0
                    self.StatusData.expectedBytes = 20
                    self.StatusData.messageReceived = ""

                    while self.StatusData.receivedBytes != self.StatusData.expectedBytes:
                        #usual loop of waiting up to the point where the number of bytes you expected are received

                        tempBuff = self.socket.recv(self.StatusData.expectedBytes)

                        if len(tempBuff) >= 0:

                            self.StatusData.messageReceived += tempBuff.decode("utf-8")
                            #decoding encoded utf-8 message

                            self.StatusData.receivedBytes += len(tempBuff)
                            #updating received bytes so the loop will eventiually cease

                    if self.StatusData.messageReceived.split()[0] == "bufferSizeTaken":
                        #if our size essage is received by the server it will send a message like 'bufferSizeTaken'
                        #if this happens, the process of sending the original message will begin

                        tempInputt = "execute!" + tempInput
                        #every input we enter will beign with execute followed by '!'
                        #which is used as a border between the headers and the body of our message

                        tempInpute = str.encode(tempInputt)

                        self.socket.send(tempInpute)

                    self.StatusData.receivedBytes = 0
                    self.StatusData.expectedBytes = 20
                    self.StatusData.messageReceived = ""

                    while self.StatusData.receivedBytes != self.StatusData.expectedBytes:
                        #our original message is sent, now we are waiting for commandTaken message
                        #which will also contain the size of the response server will eventally send
                        #so that we may know how many bytes to expect

                        tempBuff = self.socket.recv(self.StatusData.expectedBytes)

                        self.StatusData.messageReceived += tempBuff.decode("utf-8")

                        self.StatusData.receivedBytes += len(tempBuff)

                    if self.StatusData.messageReceived.split()[0] == "commandTaken":

                        self.StatusData.expectedBytes = int(self.StatusData.messageReceived.split()[1])
                        #the size of the server response is taken and set,
                        #now we will send another message to the server indicating
                        #that we know how many bytes to expect so that it may send it

                        mtbs = "waitingForResponse"

                        for i in range(0, 20):

                            if i >= len(mtbs):
                                mtbs += " "

                        #filling the message up to 20'th byte with empty space
                        #server does not posses any data of expected message so it has to be 20

                        mtbse = str.encode(mtbs)

                        self.socket.send(mtbse)

                self.StatusData.receivedBytes = 0
                self.StatusData.messageReceived = ""

                while self.StatusData.receivedBytes != self.StatusData.expectedBytes:
                    #last loop, we are waiting for server response be a status message
                    #or an entire table in our database

                    tempBuff = self.socket.recv(self.StatusData.expectedBytes)

                    if len(tempBuff) >= 0:

                        self.StatusData.messageReceived += tempBuff.decode("utf-8")

                        self.StatusData.receivedBytes += len(tempBuff)

                print("response taken:" + self.StatusData.messageReceived)



            elif self.branch == "PRE_CONNECTION":
                #this branch is used for starting the connection
                #to the entered address

                print("Enter the IP and the port you want to be connected, separated by empty spaces")

                tempInput = input()
                #the input has to be an IP followed by the port separated by an empty space

                if tempInput == "close":
                    break

                tempInputList = tempInput.split()

                self.ip = tempInputList[0]
                self.port = int(tempInputList[1])

                try:

                    self.socket.connect((self.ip,self.port))
                    #the connection will fail if no socket is listening on the given port of the given IP
                    #different reasons of failing include, not suitable args (3x tuple or array)
                    #or wrong ip, port formatting

                    print("connected successfully to the server")

                    self.branch = "CONNECTED"

                except:

                    print("An error has occurred during the connection process!")



