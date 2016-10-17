from uuid import uuid1  #For unique self path creation
import os               #For path verification

class GPIO(object):
    def __init__(
            self,
            path):
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
        self._input = os.path.join(self.path, "input") #See property path ahead
        self._output = os.path.join(self.path, "output")
        self._connections = list()
        
    #Path of the VirtualGPIO
    @property
    def path(self):
        return os.path.join(self._path, self._uuid)
        
    #Unique Identifier of the Virtual GPIO
    @property
    def uuid(self):
        return self._uuid
        
    #Path of the Input Interface
    def input(self):
        return self._input
        
    #Path of the Output Interface
    def output(self):
        return self._output
        
    
        
#Exceptions:
class PathError(Exception):
    pass
