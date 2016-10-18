from .exceptions import *
from .utils import daemonize #This is for listening
from uuid import uuid1  #For unique self path creation
import datetime         #For timing-out
import os               #For path verification
import time             #For sleeping. It's time now...
import shutil

#Folder names
INPUT = "input"
OUTPUT = "output"
CLIENTS = "clients"

#Default values
DEFAULT_TIMEOUT = datetime.timedelta(minutes=30)
DEFAULT_SLEEP = 1

TIMEOUT = DEFAULT_TIMEOUT #TODO: implement Timeout
SLEEP = DEFAULT_SLEEP

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
        return isinstance(self._virtualGPIO, VirtualGPIO)

    #~~~~~~~~~FUNCTIONS~~~~~~~~~~#
    def connect_virtual_GPIO(self, gpio):
        if isinstance(gpio, VirtualGPIO):
            self._virtualGPIO = gpio
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
        return self.__getattribute__("signal_{}".format(signal))
            
    #Base Handling functions:
    #All signals must begin with "signal_"
    def signal_connect(self, uuid, timeout):
        timeout = datetime.datetime.strptime(timeout, "%Y%m%d%H%M%S")
        self.virtualGPIO.connections[uuid] = timeout #TODO: debug this. This is going to f*ck up all.

    def signal_disconnect(self, uuid):
        self.virtualGPIO.disconnect_client(uuid)

class Signal(): #Subclass this, you fool
    pass
        
#MetaSignal!!! This is awesome! TODO: All da f*cking doc!
class MetaSignal(type): #More than a MetaSignal
    def __new__(cls, action, arg_names=list(), arg_types=list()):
        #Defining the class. I love this shit
        def __init__(obj, *args, **kwargs):
            Signal.__init__(obj)
            assert len(arg_names)==len(args)
            for index, item in enumerate(args):
                assert isinstance(item, arg_types[index])
            obj._args = args
        dct = dict()        
        dct["__init__"] = __init__
        dct["args"] = property(lambda self: self._args)
        dct["action"] = property(lambda self: self.__class__.__name__.lower())
        dct["bytearray"] = property(lambda self:
                bytearray(
                        "{}:\n".format(action.lower())+"\n".join([str(arg) for arg in self.args]),   
                        "utf-8"
                        )
               )
        return type.__new__(cls, action, (Signal, ), dct)

    def __init__(cls, action, arg_names=list(), arg_types=list()):
        type.__init__(cls, action, (Signal, ), {})
        try:
            assert len(arg_names)==len(arg_types)
        except:
            raise
        cls.arg_names = arg_names
        cls.arg_types = arg_types
        cls.action = action.lower()

ConnectSignal = MetaSignal("Connect", ("uuid", "timeout"), (str, str))
DisconnectSignal = MetaSignal("Disconnect", ("uuid", ), (str, ))
                         
#Own Errors
class VirtualGPIOError(Exception):
    pass

#Main Class of the VirtualGPIO Object
class VirtualGPIO(object):
    #~~~~~~~~~VirtualGPIO~~~~~~~~#
    #~~~~~~~~~~BUILT-IN~~~~~~~~~~#
    def __init__(
            self,
            path,
            handler=VirtualGPIOBaseHandler(),
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
        self._handler = handler
        self._handler.connect_virtual_GPIO(self)
        self._connected = False

    def __del__(self): #I thought this to be fun
        self.disconnect()
            
    #~~~~~~~~~VirtualGPIO~~~~~~~~#  
    #~~~~~~~~~PROPERTIES~~~~~~~~~#
    #Path for clients
    @property
    def clients(self):
        return os.path.join(self._path, CLIENTS)

    #True if connected
    @property
    def connected(self):
        return self._connected
    
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
        return os.path.join(self._path, self.uuid)

    #Unique Identifier of the Virtual GPIO
    @property
    def uuid(self):
        return self._uuid.hex
        
    #~~~~~~~~~VirtualGPIO~~~~~~~~#
    #~~~~~~~~~~FUNCTIONS~~~~~~~~~#
    def _raw_send(self, destination, message): #Send it anyway
        now = self.timeout()    #Twice
        if isinstance(message, str):
            message = bytearray(message, "utf-8")
        if isinstance(message, bytearray):
            file_name = "{}@{}".format(now, destination)
            file_path = os.path.join(self.output, file_name)
            with open(file_path, "wb") as message_file:
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
        now = datetime.datetime.now()
        for uuid_file_name in lsdir: #Check other connections
            if uuid_file_name != self.uuid:
                with open(os.path.join(self.clients, uuid_file_name), "r") as uuid_file:
                    timeout = datetime.datetime.strptime( 
                            uuid_file.readline().strip("\n"),
                            "%Y%m%d%H%M%S"
                            )
                    if timeout >= now:
                        self.connections[uuid_file_name] = timeout
        self.keep_alive()   #See function ahead
        os.mkdir(self.path)
        os.mkdir(self.input)
        os.mkdir(self.output)
        for connection in self.connections: #Forgot this
            signal = ConnectSignal(self.uuid, self.timeout())
            self.send(connection, signal)
        self._connected = True

    def disconnect(self):   #Say Goodbye
        if self.connected:
            # ^ This shit blocked everything!
            for connection in self.connections:
                self.send(connection, DisconnectSignal(self.uuid))
            x = int()
            while x < 10:
                try:
                    os.remove(os.path.join(self.clients, self.uuid))
                    break
                except:
                    time.sleep(SLEEP)
                    x+=1
            if x==10:
                raise DisconnectingError
            try:
                shutil.rmtree(self.path)
            except:
                pass
            self._connected = False

    def disconnect_client(self, uuid):   #It's sad, but the've said you goodbye
        try:
            del(self.connections[uuid])
        except:
            pass
            
    def keep_alive(self):    #Set next timeout
        timeout = self.timeout()     #First
        with open(os.path.join(self.clients, self.uuid), "w") as uuid_file:
            uuid_file.write(timeout)
            
    def timeout(self):           #First Golden Rule: If you use it twice, write it once.
        now = datetime.datetime.now()
        timeout = now + TIMEOUT
        timeout = timeout.strftime("%Y%m%d%H%M%S")
        return timeout #I should change all nows for timeout
        
    @daemonize
    def listen(self): #Let's listen on Input
        lsdir = list()
        while True: #This will listen almost all the messages
            if len(lsdir)>0:
                lsdir.sort()
                for message_file_name in lsdir:
                    try:
                        with open(os.path.join(self.input, message_file_name), "r") as message_file:
                            signal = message_file.readline()
                            signal = signal.strip("\n").strip(":")
                            args = list()
                            next = message_file.readline().strip("\n")
                            while next != "":
                                args.append(next)
                                next = message_file.readline().strip("\n")
                            self.handler.get_signal(signal)(*args)
                        os.remove(os.path.join(self.input, message_file_name)) #Another thing I forgot
                    except:
                        raise #By now
            lsdir = os.listdir(self.input)
            time.sleep(SLEEP)

    def run(self):
        self.connect()
        self.listen()
        
    def send(self, destination, signal): #signal from MetaSignal
        assert isinstance(signal, Signal)
        self._raw_send(destination, signal.bytearray)
