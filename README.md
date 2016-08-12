# HeartBeat
A Python client-server program for communicating sensor values over TCP sockets and displaying them using a TkInter gui.
In the 'rpi' subdirectory, you will find the actual files we used in an 'Arduino+Sensors <---> Raspberry Pi+LCD' setup.
The client and server file at the top level can be run on any PC/Mac since the Bluetooth code is not there (a periodic waveform+noise is displayed instead).

The client generates a periodic+noise signal, packs it and sends the packed data to the GUI server.
The sensor value is prefixed with 'HEART:' since this program is part of a real application that runs on Raspberry Pi and sends
many sensory data streams to the GUI server for display.

Start the GUI server program and then the client, which currently connects to the server on the same host.
If desired, change the port number in the server and client programs and use a real IP address for the server to allow the two
programs to run on different hosts.
