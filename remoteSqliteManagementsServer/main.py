from base import *

from Server.server import Server

ip = socket.gethostbyname(socket.gethostname())
#since this is the server program the ip has to be the one of this system
#it can be changed but it will render this program useless
port = 9909
#custom port number, must be within port range and not reserved for special protocols

print("The IP of this system: " + str(ip))

myServer = Server(ip,port)

if __name__ == '__main__':

    myServer.run()
