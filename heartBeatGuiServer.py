from Tkinter import *
from collections import deque

import threading
import socket
import struct


class App:

   def __init__(self, root):
      self.SCREENWIDTH  = root.winfo_screenwidth()
      self.SCREENHEIGHT = root.winfo_screenheight()
      self.CORNER_X   = 1*self.SCREENWIDTH /20
      self.CORNER_Y   = 1*self.SCREENHEIGHT/20
      self.RECT_X     = 7*self.SCREENWIDTH /10
      self.RECT_Y     = 7*self.SCREENHEIGHT/10
      self.WIDTH      = self.RECT_X+2*self.CORNER_X
      self.HEIGHT     = self.RECT_Y+2*self.CORNER_Y
      self.GRID_X     = 50
      self.GRID_Y     = 40
      self.ORG_X      = self.CORNER_X
      self.ORG_Y      = self.CORNER_Y+(self.RECT_Y/2)
      self.DELTA_X    = 4
      self.SAMPLES    = self.RECT_X/self.DELTA_X
      self.LINE_WIDTH = 3
      self.MAX_DATA   = 10.0
      self.bgColor    = "#2F4F2F"
      self.gridColor  = "#00FF00"
      self.lineColor  = "#00FF00"
      self.lock       = threading.Lock()

      self.t       = 0
      self.root    = root
      self.canvas  = Canvas(root, width=self.WIDTH, height=self.HEIGHT)
      self.canvas.pack()
      self.root.minsize(width=self.WIDTH, height=self.HEIGHT)
      self.root.maxsize(width=self.WIDTH, height=self.HEIGHT)
      self.root.resizable(width=False, height=False)
      x = (self.SCREENWIDTH  - self.WIDTH )/2
      y = (self.SCREENHEIGHT - self.HEIGHT)/2
      root.geometry('%dx%d+%d+%d' % (self.WIDTH, self.HEIGHT, x, y))

      self.data = deque([])
      for i in range(1, self.SAMPLES+1):
         self.data.append( 0.0 );


   def DrawGrid(self):
      self.canvas.create_rectangle(self.CORNER_X, self.CORNER_Y,
                                   self.CORNER_X+self.RECT_X, self.CORNER_Y+self.RECT_Y, fill=self.bgColor)
      for i in range(1, (self.RECT_Y/self.GRID_Y)):
         x1 = self.CORNER_X
         x2 = self.CORNER_X + self.RECT_X
         y1 = self.CORNER_Y + i * self.GRID_Y
         y2 = self.CORNER_Y + i * self.GRID_Y
         self.canvas.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))
      for j in range(1, (self.RECT_X/self.GRID_X)):
         x1 = self.CORNER_X + j * self.GRID_X
         x2 = self.CORNER_X + j * self.GRID_X
         y1 = self.CORNER_Y
         y2 = self.CORNER_Y + self.RECT_Y
         self.canvas.create_line(x1, y1, x2, y2, fill=self.gridColor, dash=(4,4))

   def redraw(self):
      self.DrawGrid()
      x1 = self.ORG_X
      y1 = self.ORG_Y
      with self.lock:
         for y in self.data:
            x2 = x1 + self.DELTA_X
            y2 = self.ORG_Y-(y/self.MAX_DATA)*(self.RECT_Y/2)
            if y2 < self.CORNER_Y:
               y2 = self.CORNER_Y
            if y2 > (self.CORNER_Y + self.RECT_Y):
               y2 = (self.CORNER_Y + self.RECT_Y)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.lineColor, width = self.LINE_WIDTH)
            x1 = x2
            y1 = y2

   def putSamlpe(self, f):
      with self.lock:
         self.data.append( f )
         self.data.popleft()


def getReadings(client_socket):
    unpacker = struct.Struct('10s f')
    while True:
        data = client_socket.recv(unpacker.size)
        unpacked_data = unpacker.unpack(data)
        if unpacked_data[0] == 'TERMINATE:':
           print '----- Received TERMINATE'
           return
        app.putSamlpe( unpacked_data[1] )


print '-------------------- Window Started'
root = Tk()
root.wm_title("Heart Beat Over Bluetooth (^_^)")
app = App(root)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.bind((socket.gethostname(),12397))
server_socket.bind(('',12397)) # With this, connection is NOT refused
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




