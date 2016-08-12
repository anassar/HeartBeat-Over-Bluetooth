import time

import socket
import struct
import math
import random


class Gen:

   def __init__(self):
      self.RECT_X     = 600
      self.PERIODS    = 20
      self.T          = float(self.RECT_X)/self.PERIODS
      self.TAU        = self.T/5.0
      self.ORDER      = 20
      self.DELTA_X    = 4
      self.SAMPLES    = self.RECT_X/self.DELTA_X
      self.MAX_DATA   = 10.0
      self.NOISE      = 0.5

   def getSamlpe(self, t):
      t = t%(self.T*self.PERIODS)
      f = self.TAU/self.T
      for n in range(1, self.ORDER+1):
         x=(n*math.pi)
         f += (2/x) * math.sin(x*self.TAU/self.T)*math.cos(2*x*t/self.T)
      return (f*self.MAX_DATA + random.uniform(-self.NOISE, self.NOISE))



if __name__ == "__main__":
    t = 0
    gen = Gen()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('localhost', 12397))
    packer = struct.Struct('10s f')
    try:
        while True:
            t += 1
            heartValue = gen.getSamlpe(t)
            values = ('HEART:    ', heartValue)
            packed_data = packer.pack(*values)
            client_sock.sendall(packed_data)
    finally:
        values = ('TERMINATE:', 0.0)
        packed_data = packer.pack(*values)
        client_sock.sendall(packed_data)
        client_sock.close()








