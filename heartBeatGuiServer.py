from Tkinter import *
import tkMessageBox
import random
import time
from collections import deque
import math

import threading
import socket
import struct


class App:

   def __init__(self, root):
      self.SCREENWIDTH  = root.winfo_screenwidth()
      self.SCREENHEIGHT = root.winfo_screenheight()
      self.ROWS       = 2
      self.COLS       = 2
      self.PADX       = 20
      self.PADY       = 20
      self.RECT_X     = ((7*self.SCREENWIDTH /10)/self.COLS)
      self.RECT_Y     = ((7*self.SCREENHEIGHT/10)/self.ROWS)
      self.WIDTH      = self.COLS*self.RECT_X+(self.COLS+2)*self.PADX
      self.HEIGHT     = self.ROWS*self.RECT_Y+(self.ROWS+2)*self.PADY
      self.GRID_X     = 50
      self.GRID_Y     = 40
      self.ORG_X      = 0
      self.ORG_Y      = self.RECT_Y/2
      self.PERIODS    = 20
      self.T          = float(self.RECT_X)/self.PERIODS
      self.TAU        = self.T/5.0
      self.ORDER      = 20
      self.DELTA_X    = 4
      self.SAMPLES    = self.RECT_X/self.DELTA_X
      self.LINE_WIDTH = 3
      self.MAX_DATA   = 800.0
      self.NOISE      = 0.5
      self.bgColor    = "#2F4F2F"
      self.gridColor  = "#00FF00"
      self.lineColor  = "#00FF00"
      self.lock       = threading.Lock()

      self.t       = 0
      self.root    = root
      self.canvas1 = Canvas(root, width=self.RECT_X, height=self.RECT_Y)
      self.canvas2 = Canvas(root, width=self.RECT_X, height=self.RECT_Y)
      self.canvas3 = Canvas(root, width=self.RECT_X, height=self.RECT_Y)
      self.canvas4 = Canvas(root, width=self.RECT_X, height=self.RECT_Y)
      #self.canvas1.pack()
      self.canvas1.grid(row=0, column=0, columnspan=1, rowspan=1,
               padx=self.PADX, pady=self.PADY)
      self.canvas2.grid(row=0, column=1, columnspan=1, rowspan=1,
               padx=self.PADX, pady=self.PADY)
      self.canvas3.grid(row=1, column=0, columnspan=1, rowspan=1,
               padx=self.PADX, pady=self.PADY)
      self.canvas4.grid(row=1, column=1, columnspan=1, rowspan=1,
               padx=self.PADX, pady=self.PADY)
      self.root.minsize(width=self.WIDTH, height=self.HEIGHT)
      self.root.maxsize(width=self.WIDTH, height=self.HEIGHT)
      self.root.resizable(width=False, height=False)
      x = (self.SCREENWIDTH  - self.WIDTH )/2
      y = (self.SCREENHEIGHT - self.HEIGHT)/2
      root.geometry('%dx%d+%d+%d' % (self.WIDTH, self.HEIGHT, x, y))

      self.data = deque([])
      for i in range(1, self.SAMPLES+1):
         self.data.append( 0 );


   def DrawGrid(self):
      self.canvas1.create_rectangle(0, 0, self.RECT_X, self.RECT_Y, fill=self.bgColor)
      self.canvas2.create_rectangle(0, 0, self.RECT_X, self.RECT_Y, fill=self.bgColor)
      self.canvas3.create_rectangle(0, 0, self.RECT_X, self.RECT_Y, fill=self.bgColor)
      self.canvas4.create_rectangle(0, 0, self.RECT_X, self.RECT_Y, fill=self.bgColor)
      for i in range(1, (self.RECT_Y/self.GRID_Y)+1):
         x1 = 0
         x2 = self.RECT_X
         y1 = i * self.GRID_Y
         y2 = i * self.GRID_Y
         self.canvas1.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))
         self.canvas2.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))
         self.canvas3.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))
         self.canvas4.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))
      for j in range(1, (self.RECT_X/self.GRID_X)+1):
         x1 = j * self.GRID_X
         x2 = j * self.GRID_X
         y1 = 0
         y2 = self.RECT_Y
         self.canvas1.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))
         self.canvas2.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))
         self.canvas3.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))
         self.canvas4.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))

   def redraw(self):
      self.DrawGrid()
      x1 = self.ORG_X
      y1 = self.ORG_Y
      with self.lock:
         for y in self.data:
            x2 = x1 + self.DELTA_X
            y2 = self.ORG_Y-((y/self.MAX_DATA)*(self.RECT_Y/2))
            if y2 < 0:
               y2 = 0
            if y2 > self.RECT_Y:
               y2 = self.RECT_Y
            #print '(x1, y1)-->(x2, y2) = (', x1, ',', y1, ')-->(', x2, ',', y2, ')'
            self.canvas1.create_line(x1, y1, x2, y2, fill=self.lineColor, width = self.LINE_WIDTH)
            x1 = x2
            y1 = y2

   def putSamlpe(self, f):
      with self.lock:
         self.data.append( f )
         self.data.popleft()

   def getSamlpe(self):
      f = self.TAU/self.T
      for n in range(1, self.ORDER+1):
         x=(n*math.pi)
         f += (2/x) * math.sin(x*self.TAU/self.T)*math.cos(2*x*self.t/self.T)
      return (f*self.MAX_DATA + random.uniform(-self.NOISE, self.NOISE))




WINDOW = 50
SCALE  = 20.0

def getReadings(client_socket):
    unpacker = struct.Struct('10s f')
    movingAverage = deque([])
    for i in range(1, WINDOW+1):
       movingAverage.append( 600 );
    while True:
        data = client_socket.recv(unpacker.size)
        unpacked_data = unpacker.unpack(data)
        if unpacked_data[0] == 'TERMINATE:':
           print '---- Received TERMINATE'
           return
        val = unpacked_data[1]
        #movingAverage.append( val )
        #movingAverage.popleft()
        #sumAll=0
        #for y in movingAverage:
        #   sumAll += y
        #avg = sumAll/WINDOW
        avg = 600
        val = SCALE*(unpacked_data[1]-avg)
        print "------ Received: ", val
        app.putSamlpe( val )


print '-------------------- Window Started'
root = Tk()
root.wm_title("Heart Beat Over Bluetooth (^_^)")
app = App(root)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.bind((socket.gethostname(),12397))
server_socket.bind(('',12348))
server_socket.listen(5)

# We expect one connection request.
(client_socket, address) = server_socket.accept()
t= threading.Thread(target=getReadings, args=(client_socket,))
t.daemon=True
t.start()


def redraw():
   app.redraw()
   root.after(1000, redraw) # Reschedule yourself
root.after(1000, redraw)
root.mainloop()




