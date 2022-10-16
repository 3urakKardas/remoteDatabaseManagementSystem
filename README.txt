What is it's goal?
The aim of this project was to create some kind of protocol and tool to manage a database on a device 
from another via internet connection.The system is formed of two different projects found in their respective 
directories that are found in the same folder of this log.They are differentiating in their roles, one is the server
responsabile for taking character strings from connected clients, dechypering them(we are not using the kind of
XML formated protocol but one we have created ourselves) and managing the database in accordance to the request,
and the other is the client responsabile for connecting to the server, taking user input, encrypting it to our own 
protocol and of course sending it to the server.(The system was developed as two separated pyCharm projects
and the respective files related to the IDE can be found in their directories, as it holds a comprehensive history of 
the development as well as the libraries we have used in this project, it may be useful, although all libraries used 
are found in the standart library set of python3)

How can I use it?
First of all we need to run our server.py script or it's ".compiled_python_code" application found in its directory.
Secondly we need to run our client ,these programs can be started on different computers but the user of the client must know the
IP and port value of the server, if started by default the server will posses the IP of the computer it is being run and the port 
of 9909, the port can be changed but the IP can not.After the client is started it will ask for user input,
the initial input must be an IP address followed by a port value separated by an empty space, technically the client can connect to 
any socket on the internet and it may even be used for taking input from any server, had ve not modified our message to
our custom protocol before sending it, unfortunately the chance of any other server using our protocol in that given time are very slim,
so the IP and port values we will pass have to be the values on which the server is being run, if both programs are tested on the same
computer the IP must be that of our own.If there is no empty space between our values or the format of this values are wrong
the connection will fail otherwise it will print a message indicating we are connected.Afterwards we need to connect to a database
on the computer the server is working on with the resriction of database being on the same directory as the server script.
Afterwards, with some extra keywords we may use any server implemented sqlite3 command in the folowing manner.

"connect 'example.db'" request connects to the database 'example.db' if it exists and creates one beforehand if it does not.
If we are connected a positive message will be displayed.

"execute 'SQLITECOMMAND'" request will execute 'SQLITECOMMAND' on the database we are connected, this command must mainly be used for creating,
updating, deleting elements, in short every command that does not aim reading elements.

"set:'varName' 'varValue'" request creates a variable named 'varName' having the value 'varValue' stored in the dictionary object associated with 
our connected database, we will be able to use these variables later on our requests as arguments of sqlite3 methods and they are 
also accesible to other clients connected to the same database.
('varValue' has to be entered in the literal format of the type wanted)

"append:'varName' 'varValue'" request appends 'varValue' to the list named 'varName' declared/initialized beforehand, 
this will only work when 'varName' is a list.('varValue' must again be entered as a literal)

"executemany:'varName' 'SQLITECOMMAND'" request
applies .executemany()(sqlite3 standart library for python) function on connected database and set its second argument as 'varName'.
(this method is mainly used for inserting all appropriately formatted 'varName' elements into connected database)

"print 'SQLITECOMMAND'" request gets and prints all elements got from query command 'SQLITECOMMAND'.
(the string got from this request is in the form of list literal, so the script can be modified with ease to for example create a .csv 
file and insert all elements in using another library)

"close" request ends our program.

What is going on behind?
As soon as the server is started it begin it's waiting for new connections, it is doing so by listening to its own socket.When a new
client is connected a thread possesing it's address is started, this unique thread is associated with only one client 
and is responsabile for taking requests, managing them and sending responses to it.Unless the thread is in the process of executing a commmand it will
always wait for 20 bytes ,the first response taken from the client will be of 20 bytes and will contain the size of encoded to utf-8 client request string
after this message is got the thread will send a message to the client indicating it knows how many bytes to expect and starts listening for
that amout, when the request is taken it will try to do whatever is asked in the request, if possible.Successful or not 
the thread will prepare a response and encode it to utf-8 bytes before determining its size, it then will send a message containg this value
to the client,the client is to send another message to our server inicating it's knowledge of the size of our response we are about to send,
and our final message is sent,ending the whole handshaky process of data transportation and leading the way for another sequence.

Limitations?
The abilities of this system are very limited, the reason being me wanting to move forward.
It has the potential to be expanded ,and can even be even used in daily life for not so picky clients.
Another thing that I want to add in the future is a GUI, that would certainly make the whole program more attractive and easy to use.
The easiest way would be adding another thread responsabile for graphical interface having acces to the client variables.

Notes:

On the script all variables named mtbs, mtbse, mtbsee stand for "message to be sent" and "message to be sent encoded" and 
are used as soon as they are declared just before getting obsolete, so no hard tracking is needed there.

As they are using internet connection firewall may need permission for both programs, even if not given they are usually working 
just fine, but on different platforms or under the protection of some serious security programs they can be blocked,
if so the permission must be given both on firewall and on the custom security app.

Example sequence of client-side user input:

"123.456.78.9 9909"

"connect example.db"

"execute CREATE TABLE customers (first_name text,last_name text,email text)"

"set:myList [('Johan','Liebert','jhnLibrt@email.com),('Jean','Valjean','jnVljn@email.com')]"

"append:myList ('Carolus','Rex','crlsRx@email.com')"

"executemany:myList INSERT INTO customers VALUES (?,?,?)"

"print SELECT rowid, * FROM customers"

github/3urakKardas
