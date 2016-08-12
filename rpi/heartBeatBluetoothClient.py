import time
# Example of interaction with a BLE UART device using a UART service
# implementation.
# Author: Tony DiCola
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART

import socket
import struct



# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

######################################################
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect(('localhost', 12397))
######################################################



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
    packer = struct.Struct('10s f')
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

        while True:
            # Now wait up to one minute to receive data from the device.
            #print('Waiting for next command from the device...')
            received = uart.read(timeout_sec=60)
            if received is not None:
                # Received data, print it out.
                #print('Received: {0}'.format(received))
                if (received == 'TERMINATE'):
                    break
                if (received.startswith('STRETCH:')):
                    stretchValue = received[8:]
                    print 'Stretch value = ', stretchValue
                elif (received.startswith('ACCEL:')):
                    accelValue = received[6:]
                    print 'Accelerometer value = ', accelValue
                elif (received.startswith('HEART:')):
                    heartValue = received[6:]
                    print 'Heart-signal value = ', heartValue
                    #app.putSamlpe( heartValue )
                    #queue.put( heartValue )
                    values = ('HEART:    ', float(heartValue))
                    packed_data = packer.pack(*values)
                    client_sock.sendall(packed_data)
                elif (received.startswith('TEMP:')):
                    tempValue = received[5:]
                    print 'Temperature value = ', tempValue
                else:
                    print 'Unknown command = ', received
            else:
                # Timeout waiting for data, None is returned.
                print('Received no data!')
    finally:
        # Make sure device is disconnected on exit.
        device.disconnect()
        values = ('TERMINATE:', 0.0)
        packed_data = packer.pack(*values)
        client_sock.senda11(packed_data)
        client_sock.close()
 
 
  
# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()
ble.run_mainloop_with(main)





