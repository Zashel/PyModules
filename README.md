# PyModules
Modules and Utilities for Python 3

*Virtual GPIO* is a way of communication between different computers in the same network with a shared folder imitating the way a GPIO uses a file in GNU-Linux. This is distributed and not server dedicated. No direct connection requiered between clients.

New signals are classes of metaclass BaseSignal and are created instantiating this with the name of the signal without "signal\_" and two lists: one with the name of the argument of the signal and another with the type of the argument. You may instantiate the new class to send any signal.

You can handle directly the signals subclassing VirtualGPIOBaseHandler and creating new functions with the name "signal\_" and signal name.

Instantiate VirtualGPIO, connect, and use the daemon "listen" to notice all signals, including connect and disconnect. Other stuff relies on you.

*WebSocket* is a communication interface with HTML5 websockets. Instantiate with the port, use listen to receive and send to... whatever send does.

*This "PyModules" is "deprecated". Up to fork each module in their own project.*
