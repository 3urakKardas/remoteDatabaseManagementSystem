from base import *

class StatusData:

    def __init__(self):

        self.status = "WAITING_FOR_INPUT"

        self.expectedBytes = 0
        self.receivedBytes = 0

        self.messageReceived = ""

        self.activeDatabase = ""