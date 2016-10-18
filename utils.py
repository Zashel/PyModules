import os
from threading import Thread
from .exceptions import PathError

#Not sure I wrote this code. 
#I suppose I didn't, but found it as tutorials.
#If this is yours, please, tell me.

def search_win_drive(path):
    '''
    Searches for a drive in a windows machine given a path to 
    look for from root.
    Returns the full path with the given path or raises
    PathError if not found.
    '''
    drives = "DEFGHIJKLMNOPQRSTUVWXYZ"
    for drive in drives:
        full_path = r"{}:\{}".format(drive, path)
        if os.path.exists(full_path):
            return full_path
    else:
        raise PathError        

def threadize(function):
    '''
    Make a function run asyncronously in a parallel thread.
    '''
    def inner(*args, **kwargs):
        class ThreadDeco(Thread):
            def run(self):
                function(*args, **kwargs)
        t = ThreadDeco()
        t.start()
        return t
    return inner
    _make_thread.__name__ = function.__name__

def daemonize(function):
    '''
    Make a function run asyncronously in a parallel thread
    as a hell's Daemon.
    '''
    def inner(*args, **kwargs):
        class ThreadDeco(Thread):
            def run(self):
                function(*args, **kwargs)
        t = ThreadDeco()
        t.setDaemon(True)
        t.start()
        return t
    return inner
    _make_daemon.__name__ = function.__name__
    
#For compatibilities with other modules and stuff of my own:
buscar_unidad = search_win_drive
make_thread = threadize
make_daemon = daemonize
