from .Exceptions import *
from .utils import daemonize #This is for listening
from uuid import uuid1  #For unique self path creation
import datetime         #For timing-out
import os               #For path verification
import time             #For sleeping. It's time now...

#Folder names
INPUT = "input"
OUTPUT = "output"
CLIENTS = "clients"

#Default values
DEFAULT_TIMEOUT = datetime.timedelta(minutes=30)
DEFAULT_SLEEP = 1

TIMEOUT = DEFAULT_TIMEOUT
SLEEP = DEFAULT_SLEEP

#Main Class of the VirtualGPIO Object
class VirtualGPIO(object):
    #~~~~~~~~~VirtualGPIO~~~~~~~~#
    #~~~~~~~~~~BUILT-IN~~~~~~~~~~#
    def __init__(
            self,
            path,
            handler=VirtualGPIOBaseHandler()
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
        handler.connect_virtual_GPIO(self)
        self._handler = handler
        self._exit = False

    def __del__(self): #I thought this to be fun
        while True:
            try:
                self.disconnect()
                break
            except:
                pass #TODO: ask for action. Which one? Aaaaaah
        time.sleep(SLEEP)
        
            
    #~~~~~~~~~VirtualGPIO~~~~~~~~#  
    #~~~~~~~~~PROPERTIES~~~~~~~~~#
    #Path for clients
    @property
    def clients(self):
        return os.path.join(self._path, CLIENTS)
    
    #Handler
    @property
    def handler(self):
        return self._handler
        
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
        
    #~~~~~~~~~VirtualGPIO~~~~~~~~#
    #~~~~~~~~~~FUNCTIONS~~~~~~~~~#
    def _raw_send(destination, message): #Send it anyway
        now = self.now()    #Twice
        if isinstance(message, str):
            message = bytearray(message, "utf-8")
        if isinstance(message, bytearray):
            file_name = "{}@{}".format(now, destination)
            file_path = os.path.join(self.output, file_name)
            with open(file_path, "rb") as message_file:
                message_file.write(message)
            destination_path = os.path.join(
                    self._path, 
                    destination,
                    INPUT,
                    file_name) #Now we move the data.
            try:
                os.rename(file_path, destination_path)
            except:
                raise Exception #Look for an Exception
        else:
            return TypeError("message must be a bytearray or a str")
            
    def connect(self):      #Make file and GPIO Visible
        if not os.path.exists(self.clients):
            os.mkdir(self.clients)
        lsdir = os.listdir(self.clients)
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

    def disconnect(self):   #Say Goodbye
        slef._exit = True
        for connection in self.connections:
            self.send(connection, DisconnectSignal())
        x = int()
        while x < 10:
            try:
                os.remove(os.path.path.join(self.clients, self.uuid))
                break
            except:
                time.sleep(SLEEP)
                x+=1
        if x==10:
            raise DisconnectingError

    def disconnect_client(self, uuid):   #It's sad, but the've said you goodbye
        try:
            del(self.connections[uuid])
        except:
            pass
            
    def keep_alive(self):    #Set next timeout
        now = self.now()     #First
        with open(os.path.join(self.clients, self.uuid), "w") as uuid_file:
            uuid_file.write(now)
            
    def now(self):           #First Golden Rule: If you use it twice, write it once.
        now = datetime.datetime.now()
        timeout = now + TIMEOUT
        timeout = timeout.strftime("%Y%m%d%H%M%S")
        return now
        
    @daemonize
    def listen(self): #Let's listen on Input
        lsdir = list()
        while (not self._exit or len(lsdir)>0): #This will listen almost all the messages
            if len(lsdir)>0:
                lsdir.sort()
                for message_file_name in lsdir:
                    try:
                        with open(os.path.join(self.input, message_file_name), "r") as message_file:
                            signal = message_file.readline().strip("\n").strip(":")
                            args = list()
                            next = message_file.readline().strip("\n")
                            while next != "":
                                args.append(next)
                                next = message_file.readline().strip("\n")
                                self.handler.get_signal(signal)(*args)
                    except:
                        raise #By now
            lsdir = os.listdir(self.input)
            time.sleep(SLEEP)
        
    def send(destination, signal): #signal from BaseSignal
        assert isinstance(signal, BaseSignal)
        self._raw_send(destination, signal.bytearray)
        
        
#Virtual GPIO Handler
class VirtualGPIOBaseHandler(object):   #To be subclassed to handle the GPIO and other Stuff
    #~~~~~~~~~~BUILT-IN~~~~~~~~~~#
    def __init__(self):
        '''
        You must subclass it to handle the GPIO and other Stuff
        '''
        self._virtualGPIO = None
        self._connected_stuff = dict()
        
    def __getattr__(self, key):
        if key in self._connected_stuff:
            return self._connected_stuff[key]
        else:
            raise AttributeError
    #~~~~~~~~~PROPERTIES~~~~~~~~~#
    @property
    def virtualGPIO(self):
        return self._virtualGPIO
    
    @property
    def is_connected(self):
        return isinstance(self._vitualGPIO, VirtualGPIO)

    #~~~~~~~~~FUNCTIONS~~~~~~~~~~#
    def connect_virtual_GPIO(self, gpio):
        if isinstance(gpio, VirtualGPIO):
            self._VirtualGPIO = gpio
        else:
            raise VirtualGPIOError
            
    def connect_stuff(self, **kwargs):
        '''
        Yes, Stuff, You can handle other app if you like.
        If you name it "app" you can access it with handle.app
        '''
        for kwarg in kwargs:
            self._connected_stuff[kwarg] = kwargs[kwarg]
            
    def get_signal(self, signal):
        return self.__getattr__("signal_{}".format(signal))
            
    #Base Handling functions:
    #All signals must begin with "signal_"
    def signal_connect(self, uuid, timeout):
        self.virtualGPIO.connections[uuid] = timeout

    def signal_disconnect(self, uuid):
        self.virtualGPIO.disconnect_client(uuid)
        
#BaseSignal!!! This is awesome! TODO: All da f*cking doc!
class BaseSignal(type): #More than a BaseSignal
    def __new__(cls, action, arg_names=list(), arg_types=list()):
        assert len(arg_names)==len(arg_types)
        cls.arg_names = arg_names
        cls.arg_types = arg_types
        #Defining the class. I love this shit
        def __init__(obj, *args, **kwargs):
            assert len(arg_names)==len(args)
            for index, item in enumerate(args):
                assert isinstance(item, obj.__class__.arg_types[index])
            obj._args = args
        dct = dict()        
        dct["__init__"] = __init__
        dct["args"] = property(lambda self: self._args)
        dct["action"] = property(lambda self: self.__class__.__name__.lower())
        dct["bytearray"] = property(lambda self:
                bytearray(
                        "{}:\n".format(self.action)+"\n".join([str(arg) for arg in self.args]),   
                        "utf-8"
                        )
               )
        return type.__new__(cls, action, (), dct)

ConnectSignal = BaseSignal("Connect")
DisconnectSignal = BaseSignal("Disconnect")
                         
#Own Errors
class VirtualGPIOError(Exception):
    pass
