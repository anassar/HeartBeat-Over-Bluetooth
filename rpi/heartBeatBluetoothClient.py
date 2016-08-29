import time
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART

import socket
import struct
import collections


# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect(('', 12346))



WINDOW=200 # Choose this so that only one step can be inside the window

qx = collections.deque()
qy = collections.deque()
qz = collections.deque()
for i in range(1, WINDOW+1):
    qx.append(0)
    qy.append(0)
    qz.append(0)


peakFound = False
StepCount = 0

def detectPeak(q):
    val0 = None
    val1 = None
    val2 = None
    for val in q:
        val0 = val1
        val1 = val2
        val2 = val
        if val1 is None:
            continue
        if val0 is None:
            continue
        if val1 <= val0:
            continue
        if val1 <= val2:
            continue
        return True
    return False

def handleMessage(msg):
    packer = struct.Struct('10s f f f')
    if (msg == 'TERMINATE'):
        return False
    if (msg.startswith('STRETCH:')):
        stretchValue = msg[8:]
        print 'Stretch value = ', stretchValue
        values = ('STRETCH:  ', float(stretchValue), 0, 0)
        packed_data = packer.pack(*values)
        client_sock.sendall(packed_data)
    elif (msg.startswith('ACCEL:')):
        accelValue = msg[6:]
        print 'Accelerometer value = ', accelValue
        vals = accelValue.split(",")
        values = ('ACCEL:    ', float(vals[0]), float(vals[1]), float(vals[2]))
        packed_data = packer.pack(*values)
        client_sock.sendall(packed_data)
        qx.append(vals[0])
        qy.append(vals[1])
        qz.append(vals[2])
        qx.popleft()
        qy.popleft()
        qz.popleft()
        peakFoundX = detectPeak(qx)
        peakFoundY = detectPeak(qy)
        peakFoundZ = detectPeak(qz)
        if not peakFound:
            if peakFoundX or peakFoundY or peakFoundZ: # Peak entry condition
                StepCount += 1
                peakFound = True
                print( "Step Count = ", StepCount )
        elif not (peakFoundX or peakFoundY or peakFoundZ): # Peak exit condition
            peakFound = False
    elif (msg.startswith('MAG:')):
        magValue = msg[4:]
        print 'Magentometer value = ', magValue
        vals = magValue.split(",")
        values = ('MAG:      ', float(vals[0]), float(vals[1]), float(vals[2]))
        packed_data = packer.pack(*values)
        client_sock.sendall(packed_data)
    elif (msg.startswith('HEART:')):
        heartValue = msg[6:]
        print 'Heart-signal value = ', heartValue
        values = ('HEART:    ', float(heartValue), 0, 0)
        packed_data = packer.pack(*values)
        client_sock.sendall(packed_data)
    elif (msg.startswith('TEMP:')):
        tempValue = msg[5:]
        print 'Temperature value = ', tempValue
        values = ('TEMP:     ', float(tempValue), 0, 0)
        packed_data = packer.pack(*values)
        client_sock.sendall(packed_data)
    else:
        print 'Unknown command = ', msg
    return True




def getMessage(uart, leftover):
    # Now wait up to one minute to receive data from the device.
    # print('Waiting for next command from the device...')
    msg = leftover
    while True:
        received = uart.read(timeout_sec=60)
        if received is not None:
            #print "Received: " + received
            index = received.find("#") # Look up message termination
            #print "Index: " + str(index)
            if index < 0:
                msg = msg + received
            else:
                if index > 0:
                    msg = msg + received[0:index]
                if len(received) > (index+1): # Termination is not last character
                    leftover = received[index+1:]
                else:
                    leftover = ""
                break
        else:
            # Timeout waiting for data, None is returned.
            print('Received no data!')
    #print "Message: " + msg
    #print "Leftover: " + leftover
    return (msg, leftover)



# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.
def main():

    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        device = UART.find_device()
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                      # to change the timeout.

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        print('Discovering services...')
        UART.discover(device)

        # Once service discovery is complete create an instance of the service
        # and start interacting with it.
        uart = UART(device)

        # Write a string to the TX characteristic.
        uart.write('Hello world!\r\n')
        print("Sent 'Hello world!' to the device.")

        leftover = ""
        while True:
            msg, leftover = getMessage(uart, leftover)
            success = handleMessage(msg)
            if not success:
                break
    finally:
        # Make sure device is disconnected on exit.
        device.disconnect()
        values = ('TERMINATE:', 0.0, 0.0, 0.0)
        packer = struct.Struct('10s f f f')
        packed_data = packer.pack(*values)
        client_sock.senda11(packed_data)
        client_sock.close()
 
 
  
# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()
ble.run_mainloop_with(main)





