import numpy as np
import Image, ImageTk
import Tkinter as tk

#
#   GUI
#

size = (50,50)
scale = 15
winx,winy = size[0]*scale, size[1]*scale
root = tk.Tk()
w,h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry('%dx%d+%d+%d'%(winx, winy+26, w/2-winx/2, h/2-winy/2-13))
root.resizable(0,0)
root.title("Conway's Game of Life")

# Canvas
canvas = tk.Canvas(root,width=winx,height=winy,bd=-2)
canvas.grid(row=1,column=1,columnspan=3,sticky=tk.E+tk.W+tk.S+tk.N)
canvas.configure(background='black')

# Start Button
PAUSED = True
def btnfn_go(callback=None):
  'Start the automata'
  global PAUSED
  if PAUSED:
    PAUSED = False
    canvas_updater()
    btn_go.configure(text='Pause')
  else:
    PAUSED = True
    btn_go.configure(text='Start')

btn_go = tk.Button(root,text="Start",command=btnfn_go)
btn_go.grid(row=2,column=1,sticky=tk.E+tk.W)

# Re seed button
def btnfn_seed(callback=None):
  seed()

btn_seed = tk.Button(root,text="Re-Seed",command=btnfn_seed)
btn_seed.grid(row=2,column=2,sticky=tk.E+tk.W)

# Clear button
def btnfn_clr(callback=None):
  global data,prevdata,PAUSED
  data = np.copy(blankdata)
  prevdata = np.copy(blankdata)
  PAUSED = True
  btn_go.configure(text='Start')

btn_clr = tk.Button(root,text="Clear",command=btnfn_clr)
btn_clr.grid(row=2,column=3,sticky=tk.E+tk.W)

#
#   Automata
#

blankdata = np.array( np.zeros(size, dtype=int) )
data = np.copy(blankdata)

# seed the top left corner of the data with garbage
from random import randint
nbhds_to_check=[]
def seed():
  dx = size[0]/8
  midx = size[0]/2
  dy = size[1]/8
  midy = size[1]/2
  for i in xrange(midx - dx, midx + dx):
    for j in xrange(midy - dy, midy + dy):
      r=randint(0,1)
      data[i,j] = r
      if r: nbhds_to_check.append((i,j))
seed()

def get_data(x,y):
  'deal with index errors'
  # if indeces are in the array
  if 0 <= x <= size[0]-1 and 0 <= y <= size[1]-1:
    return data[x,y]
  else:
    return 0

def conway(x,y):
  "iterate using modified Conway's rules"
  state = data[x,y]
  nums = [get_data(x-1,y-1) , get_data(x,y-1) , get_data(x+1,y-1),
          get_data(x-1,y)   , 0               , get_data(x+1,y),
          get_data(x-1,y+1) , get_data(x,y+1) , get_data(x+1,y+1)]
  num = sum(nums)
  if state == 1:
    # Any live cell with fewer than two live neighbours dies, as if caused by under-population.
    if num < 2:       return 0
    # Any live cell with two or three live neighbours lives on to the next generation.
    if 2 <= num <= 3: return 1
    # Any live cell with more than three live neighbours dies, as if by overcrowding.
    if num > 3:       return 0
  # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
  elif state == 0 and num == 3: return 1
  # Else do nothing
  else: return state

new_nbhds=None
def step(rule):
  'step the automata'
  global data,nbhds_to_check,new_nbhds
  new_nbhds = []
  newdata = np.copy(blankdata)
  for tup in nbhds_to_check:
    (x,y)=tup
    # Check nine elements of the nbhd
    #   ( the point (x,y) and the 8 adjacent squares )
    for i in xrange(-1,2):
      for j in xrange(-1,2):
        xindex = x+i
        yindex = y+j
        # if indeces are in the array
        if 0 <= xindex <= size[1]-1 and 0 <= yindex <= size[0]-1:
          dat = rule(xindex,yindex)
          newdata[xindex,yindex] = dat
          if dat == 1 and (xindex,yindex) not in new_nbhds:
            # if living, add to new nbhds
            new_nbhds.append((xindex,yindex))
  nbhds_to_check = new_nbhds
  data = newdata

#
#   Run
#

imgTk = None
canv_im = None
def canvas_updater():
  # apply rule to all pixels
  step( conway )
  # Fix up data
  imdata = 255*data
  imdata = np.kron( imdata, np.ones((scale,scale),dtype=int) )
  # Make image
  img = Image.fromarray( imdata )
  # make PIL image tk friendly, Add to canvas
  global imgTk, canv_im, canvas # don't want these garbage collected
  imgTk = ImageTk.PhotoImage( img )
  canvas.delete( canv_im )
  canv_im = canvas.create_image(0,0,anchor='nw',image=imgTk)
  global PAUSED
  if not PAUSED:
    root.after(50, canvas_updater)

tk.mainloop()
