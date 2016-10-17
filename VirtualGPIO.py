from .Exceptions import *
from uuid import uuid1  #For unique self path creation
import datetime         #For timing-out
import os               #For path verification

#Folder names
INPUT = "input"
OUTPUT = "output"
CLIENTS = "clients"

#Default values
DEFAULT_TIMEOUT = datetime.timedelta(minutes=30)

#Main Class of the VirtualGPIO Object
class VirtualGPIO(object):
    #~~~~~~~~~~BUILT-IN~~~~~~~~~~#
    def __init__(
            self,
            path,
            *,
            timeout = DEFAULT_TIMEOUT):
        '''
        Instantiate a Virtual GPIO.
        
        path: path for the required files to be created/modified
        '''
        if not os.path.exists(path):
            raise PathError(
                    "Path {} does not exist".format(
                            path
                    )
            )
        self._path = path
        self._uuid = uuid1()
        self._input = os.path.join(self.path, INPUT)    #See property path ahead
        self._output = os.path.join(self.path, OUTPUT)
        self.connections = dict()
        
    #~~~~~~~~~~PROPERTIES~~~~~~~~~~#
    #Path for clients
    @property
    def clients(self):
        return os.path.join(self._path, CLIENTS)
        
    #Path of the Input Interface
    @property
    def input(self):
        return self._input
        
    #Path of the Output Interface
    @property
    def output(self):
        return self._output
                
    #Path of the VirtualGPIO
    @property
    def path(self):
        return os.path.join(self._path, self._uuid)

    #Unique Identifier of the Virtual GPIO
    @property
    def uuid(self):
        return self._uuid

    #~~~~~~~~~~FUNCTIONS~~~~~~~~~~#
    def connect(self):      #Make file and GPIO Visible
        if not os.path.exists(self.clients):
            os.mkdir(self.clients)
        lsdir = os.lsdir(self.clients)
        for uuid_file_name in lsdir: #Check other connections
            if uuid_file_name != self.uuid:
                with open(os.path.join(self.clients, uuid_file_name), "r") as uuid_file:
                    now = datetime.datetime.now()
                    timeout = datetime.datetime.strptime( 
                            uuid_file.readline().strip("\n"),
                            "%Y%m%d%H%M%S"
                            )
                    if timeout >= now:
                        self.connections[uuid_file_name] = timeout
        self.keep_alive()   #See function ahead
            
    def keep_alive(self):    #Set next timeout
        now = self.now()     #First
        with open(os.path.join(self.clients, self.uuid), "w") as uuid_file:
            uuid_file.write(now)
            
    def now(self):           #First Golden Rule: If you use it twice, write it once.
        now = datetime.datetime.now()
        timeout = now + DEFAULT_TIMEOUT
        timeout = timeout.strftime("%Y%m%d%H%M%S")
        return now
    
    def send(destination, message): #Send it anyway
        now = self.now()    #Twice
        if isinstance(message, str):
            message = bytearray(message, "utf-8")
        if isinstance(message, bytearray):
            file_name = "{}@{}".format(now, destination)
            file_path = os.path.join(self.output, file_name)
            with open(file_path, "rb") as message_file:
                message_file.write(message)
        else:
            return TypeError("message must be a bytearray or a str")
        
#Virtual GPIO Handler
class VirtualGPIOBaseHandler(object):   #To be subclassed to handle the GPIO and other Stuff
    def __init__(self):
        self._VirtualGPIO = None
        
    def connect_virtual_GPIO(self, gpio):
        if isinstance(gpio, VirtualGPIO):
            self._VirtualGPIO = gpio
        else:
            raise VirtualGPIOError
            
#Own Errors
class VirtualGPIOError(Exception):
    pass
