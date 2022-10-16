import threading

from base import *

class Server:

    def __init__(self,ip,port):

        self.lock = threading.Lock()
        #used for synchronised management of the object share by multiple threads
        #necessity is dependent on the system

        self.listOfDatabases = {}
        #stores the databases found in the same file as this script
        #every .db file in the directory is added here as a key and value where key is the name of the file
        #and value is another dictionary storing several attributes related to the database
        #(example.db["cursor"] stores the cursor object created during runtime, every db onject has one
        #examle.db["var"] stores the value of a variable named var that was set by the client,
        #not every db has to have one)
        #also every .db file created during runtime with a call from client is also added here

        for file in os.listdir(os.path.dirname(sys.argv[0])):
            #this loop is responsabile for getting all absolute paths of files in the same directory
            #of the script being run, checking whether the second term tokenized by '.' is equal to 'db'
            #(this is important since it also means no .db file containg '.' within its name
            #will be loaded at the beginning of the server, although this kind of database will be saved
            #when being created for the first time and can even be used by multiple clients)
            #and if so adding it to self.listOfDatabases

            if len(file.split(".")) >= 2 and file.split(".")[1] == "db":

                tempConn = sqlite3.connect(file,check_same_thread=False)

                tempCursor = tempConn.cursor()

                self.listOfDatabases[file] = {"db":tempConn,"cursor":tempCursor}

        self.shouldClose = False

        self.ip = ip
        self.port = port

        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #main socket, responsabile for waiting and listening for new connections,
        #all clients will be accepted through this object

        self.socket.bind((self.ip,self.port))

        self.listOfClientThreads = []
        #stores all threads responsabile for handling every individual client,
        #since we are using non blocking sockets we have to use threads so that responses
        #to clients will be fast enough, not doing so will let the only alternative
        #be a linear management method involving evry client waiting for another to end its request
        #which will render the program slow and unusable, especially for a large amount of users in any given time

    def manageClient(self,clientSocketAddressTuple,threadIndex):
        #since this is the function used for individual client management, every variable
        #declared in this scope will be unique to every thread and in turn every client
        #thus we do not need any client class in this server program

        global threadShouldClose
        threadShouldClose = False

        flags = {"status":"WAITING_FOR_BUFFER_SIZE"}
        #everything related to our thread is stored here

        clientSocket = clientSocketAddressTuple[0]
        #this object will be used for sending and receiving data to and from the client

        global expectedBytes

        global receivedBytes
        receivedBytes = 0

        global messageBuffer
        messageBuffer = ""

        global responseMessage

        global tempBuff
        #used for pieces of data we got through the socket
        #every piece will eventually be compounded ino a single 'messageBuffer'
        #global declared for common usage on different status branches

        global connectedDataBase
        connectedDataBase = None
        #if our user is connected to a database, this will be set to the value of a database name
        #stored in self.listOfDatabases

        #-----------------------------------------NOTE-------------------------------------------------------------
        #all of the global declarations could have been avoided had we use a method
        #similar to the one we did in the client.py, this one can not be said
        #to be faster but an alternative which does not decrease the practical(but theoretical) efficiency
        #even for large amounts of clients

        while not threadShouldClose:

            if flags["status"] == "WAITING_FOR_BUFFER_SIZE":
                #while client is not making any request this thread will always be expecting 20 bytes
                #which when got, will contain the size of original client request

                expectedBytes = 20

                while receivedBytes != expectedBytes:
                    # usual loop of waiting up to the point where the number of bytes you expected are received

                    tempBuff = clientSocket.recv(expectedBytes)

                    if len(tempBuff) > 0:

                        messageBuffer += tempBuff.decode("utf-8")#utf-8

                        receivedBytes += len(tempBuff)

                    if str(tempBuff) == "b''":
                        #the disconnected sockets will be sending the message of b''
                        #when this message is got it means that the client is not connected anymore
                        #and the 'not needed anymore' thread should be closed, as not to use
                        #any unnecessary computational power

                        threadShouldClose = True

                        break

                if not threadShouldClose and messageBuffer.split()[0] == "bufferSize":

                    expectedBytes = int(messageBuffer.split()[1]) + 8

                    mtbs = "bufferSizeTaken"

                    for i in range(0, 20):

                        if i >= len(mtbs):
                            mtbs += " "

                    #we are sending a message to the client indicating that we know how many bytes to expect
                    #and it may send the message, since it will, too, wait for 20 bytes we are filling the string
                    #with empty spaces, up to the expected size

                    mtbss = str.encode(mtbs)
                    # encoding entered string into an utf-8 binary format that unlike the name suggests,
                    # in most cases is comprising of more than 8 bytes and can map lots of characters
                    # not being represented is ASCII, like the ones found in Turkish, Chinese and Russian languages

                    clientSocket.send(mtbss)

                    flags["status"] = "WAITING_FOR_COMMAND"

            elif flags["status"] == "WAITING_FOR_COMMAND":
                #since we have sent the message indicating we are ready,
                #the client will eventally be sending it original request
                #if it is disconnected during this or any similar process this thread will be closed during
                #the expecting byte process

                while receivedBytes != expectedBytes:

                    tempBuff = clientSocket.recv(expectedBytes)

                    messageBuffer += tempBuff.decode("utf-8")

                    receivedBytes += len(tempBuff)

                    if str(tempBuff) == "b''":

                        threadShouldClose = True

                        break

                if not threadShouldClose and messageBuffer.split("!")[0] == "execute":
                    #checking if the request string starts with 'execute', this word
                    #is added at the beginning of client request automatically and is used as a secondary
                    #mechanism for determining whether the request has been delivered correctly,
                    #although it is not going to differ much since our sockets are using tcp protocol
                    #the only kind error of this manner may be caused by garbage characters got

                    responseMessage = "no suitable message " + messageBuffer.split("!")[1]
                    #this message will reach the end of conditions if none of them suits, and so it will be sent

                    commandList = messageBuffer.split("!")

                    try:
                        #tries to execute commands related to sqlite3 in accordance to request got from the client
                        #using multi threaded database management may cause ample of exceptions

                        #the below conditioning is executing commands by dissecting the request message
                        #in accordance to pre-determined protocol we have agreed upon
                        if messageBuffer.split("!")[1] == "connect":
                            #a request got in the form 'execute!connect!example.db' which
                            #will be mapped/transformed from user entered message 'connect example.db'
                            #connects the thread related to the client the request was made from
                            #to the database named example.db,
                            #if there is no such database 'example.db' in the same directory
                            #as this folder, a new one will be created
                            #from the point on, of creation, even during the runtime, the new
                            #databse will be accessible to other clients

                            try:

                                if messageBuffer.split("!")[2] in self.listOfDatabases:

                                    connectedDataBase = self.listOfDatabases[messageBuffer.split("!")[2]]

                                    responseMessage = "the database is connected"

                                else:

                                    tempConn = sqlite3.connect(messageBuffer.split("!")[2],check_same_thread=False)

                                    tempCursor = tempConn.cursor()

                                    tempDB = {"db":tempConn,"cursor":tempCursor}

                                    self.listOfDatabases[messageBuffer.split("!")[2]] = tempDB

                                    connectedDataBase = self.listOfDatabases[messageBuffer.split("!")[2]]

                                    responseMessage = "the database was created and connected"

                            except:

                                responseMessage = "An error has occurred during execute call!"

                        elif connectedDataBase != None and commandList[1] == "execute":
                            #a request got in the form 'execute!execute!"SQL COMMAND"' which
                            #will be mapped/transformed from user entered message 'execute "SQL COMMAND"'
                            #will execute any sqlite3 command "SQL COMMAND" that aims the modification
                            #of the connected database, if no database is associated with the client
                            #this request will not have any effect

                            try:

                                connectedDataBase["cursor"].execute(commandList[2])

                                connectedDataBase["db"].commit()

                                responseMessage = "Execution of command successful"

                            except:

                                responseMessage = "An error has occurred during execution of command!"

                        elif connectedDataBase != None and commandList[1].split(":")[0] == "set":
                            #a request got in the form 'execute!set:"varName"!"varValue"' which
                            #will be mapped/transformed from user entered message 'set:"varName" "varValue"'
                            #will create a variable named varName carrying the value varValue
                            #in the form of dictionary element stored in connected database object
                            #of which the client request came from is associated with

                            try:

                                connectedDataBase[commandList[1].split(":")[1]] = eval(commandList[2])

                                responseMessage = str(connectedDataBase[commandList[1].split(":")[1]])

                                responseMessage = "The variable is set successfully!"

                            except:

                                responseMessage = "An error has occurred during the setting of variable!"

                        elif connectedDataBase != None and commandList[1].split(":")[0] == "append":
                            #a request got in the form 'execute!append:"varName"!"varValue"' which
                            #will be mapped/transformed from user entered message 'append:"varName" "varValue"'
                            #will, in the case of the pre-declared variable named varName stored in
                            #currently connected database object of the client the request came from
                            #is associated with being an array, will append the varValue to that variable
                            #in the case where either the varName does not exist in current database object
                            #or was declared in a different database, or where varValue is not an array
                            #it will render an error and send the exception message instead

                            try:

                                if isinstance(connectedDataBase[commandList[1].split(":")[1]],list):

                                    connectedDataBase[commandList[1].split(":")[1]].append(eval(commandList[2]))

                                    responseMessage = str(connectedDataBase[commandList[1].split(":")[1]])

                                else:

                                    responseMessage = "the variable was not appended"

                            except:

                                responseMessage = "An error has occurred during append call!"

                        elif connectedDataBase != None and commandList[1].split(":")[0] == "executemany":
                            #a request got in the form 'execute!executemany:"varName"!"SQL COMMAND"' which
                            #will be mapped/transformed from user entered message 'executemany:"varName" "SQL COMMAND"'
                            #it will add all elements in the array 'varName' formed of
                            #appropriate shaped/typed members so that it will fit in to the "SQL COMMAND" given,
                            #or in a more simply way, this request will call .executemany()(sqlite3) function
                            #on connected database with primary and secondary args being "SQL COMMAND" and "varName"
                            #in the case where any of the assumptions above is not met it will render its exception

                            try:

                                if commandList[1].split(":")[1] != None:

                                    connectedDataBase["cursor"].executemany(commandList[2],connectedDataBase[commandList[1].split(":")[1]])

                                    connectedDataBase["db"].commit()

                                    responseMessage = "executemany did worked!"

                                else:

                                    responseMessage = "executemany did not work!"

                            except:

                                responseMessage = "An error has occurred during executemany call!"

                        elif connectedDataBase != None and commandList[1] == "print":
                            #a request got in the form 'execute!print!"SQL COMMAND"' which
                            #will be mapped/transformed from user entered message 'print "SQL COMMAND"'
                            #will, in the case where "SQL COMMAND" is a querying call,
                            #fetch all the elements associated with the query and send them
                            #as an array of table elements to the client

                            try:

                                connectedDataBase["cursor"].execute(commandList[2])

                                responseMessage = str(connectedDataBase["cursor"].fetchall())

                            except:

                                responseMessage = "An error has occurred during select call!"

                        #self.lock.acquire(True)
                        #the lock object was needed in different phases of this project,
                        #the necessity of it and its aquiring/releasing mechanism
                        #may differ depending on the hardware and os of the system

                    finally:

                        pass

                        #self.lock.release()

                    responseMessageEncoded = responseMessage.encode("utf-8")

                    mtbs = "commandTaken " + str(len(responseMessageEncoded))
                    #server is sending the size of the encoded message that was got from executing phase

                    for i in range(0,20):

                        if i >= len(mtbs):

                            mtbs += " "

                    mtbss = str.encode(mtbs)

                    clientSocket.send(mtbss)

                    flags["status"] = "WAITING_FOR_SEND_COMMAND"

            elif flags["status"] == "WAITING_FOR_SEND_COMMAND":

                expectedBytes = 20

                while receivedBytes != expectedBytes:

                    tempBuff = clientSocket.recv(expectedBytes)

                    if len(tempBuff) > 0:
                        messageBuffer += tempBuff.decode("utf-8")

                        receivedBytes += len(tempBuff)

                    if str(tempBuff) == "b''":

                        threadShouldClose = True

                        break

                if not threadShouldClose and messageBuffer.split()[0] == "waitingForResponse":
                    #the server knows that the client is expecting as many bytes as we have to send,
                    #it may as well start sending them

                    clientSocket.send(responseMessageEncoded)

                    flags["status"] = "WAITING_FOR_BUFFER_SIZE"

            messageBuffer = ""

            receivedBytes = 0

        self.listOfClientThreads.pop(threadIndex)
        #if the main loop of getting input from client is over,
        #and the thread about to end, for different reasons,
        #this thread object will be erased from the list it is contained

    def run(self):

        self.socket.listen()
        #the server sockets starts listening for new connections

        while not self.shouldClose:

            print("waiting...")

            tempClientSocketAddress = self.socket.accept()
            #as soon as somebody is connected to our server socket, associeted
            #with the IP of this system and a mostly custom port,
            #we will have them stored as a tuple whose first element
            #is a socket object associeted with a number used for all data transportation between
            #the client and server, and an address containg its IP too

            tempClientThread = Thread(target=self.manageClient,args=(tempClientSocketAddress,len(self.listOfClientThreads),))
            #all of clients connected will have a thread start for them immediately that will
            #also contain their socket/address tuple

            self.listOfClientThreads.append(tempClientThread)

            tempClientThread.start()

