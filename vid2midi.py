import time, curses
import cv2
import numpy as np
import sys
from collections import namedtuple
from mido import Message, MidiFile, MidiTrack, second2tick

try:
    infile = str(sys.argv[1])
    midifile = infile.split('.')[0] + '.mid'
except:
    print ("bad input argument")
    print (str(sys.argv))
    sys.exit()

cap = cv2.VideoCapture(infile)
fps = cap.get(cv2.CAP_PROP_FPS)
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
framecount = cap.get(cv2.CAP_PROP_FRAME_COUNT)


mid = MidiFile()
mid.ticks_per_beat = 480
mid.tempo = 500000
track = MidiTrack()
mid.tracks.append(track)

BLevel = namedtuple("BLevel", ['brange', 'bval'])
_blevels = [
    BLevel(brange=range(0, 21), bval=60),
    BLevel(brange=range(20, 43), bval=61),
    BLevel(brange=range(42, 67), bval=62),
    BLevel(brange=range(66, 85), bval=63),
    BLevel(brange=range(84, 107), bval=64),
    BLevel(brange=range(106, 128), bval=65),
    BLevel(brange=range(127, 149), bval=66),
    BLevel(brange=range(148, 170), bval=67),
    BLevel(brange=range(169, 192), bval=68),
    BLevel(brange=range(191, 213), bval=69),
    BLevel(brange=range(212, 234), bval=70),
    BLevel(brange=range(233, 256), bval=71),
]

def detect_level(h_val):
    h_val = int(h_val)
    for blevel in _blevels:
      if h_val in blevel.brange:
        return blevel.bval

def ticker(t_val):
    ticks = int(second2tick(t_val, mid.ticks_per_beat, mid.tempo))
    return ticks

frametime = 1/fps
ticktime = ticker(frametime)
elapsed = 0

if (cap.isOpened()== False): 
  print("Error opening video stream or file")

fstack = [0]
estack = [0]
prenoteVal = 0
notebegin = 0

while(cap.isOpened()):

  ret, frame = cap.read()
  if ret == True:

    p = 30
    l = int(w/2)-p
    r = int(w/2)+p
    t = int(h/2)-p
    b = int(h/2)+p
    chunk = frame[l:r, t:b]
    blurchunk = cv2.GaussianBlur(chunk,(15,15),0)

    cv2.imshow('vframe', blurchunk)

    hsv = cv2.cvtColor(chunk, cv2.COLOR_BGR2HSV)
    _, _, v = cv2.split(hsv)

    avg = int(np.average(v.flatten()))
    noteVal = detect_level(avg)
    
    fstack.append(noteVal)
    estack.append(elapsed)
    if (len(fstack) > 5):
      fstack.pop(0)
      estack.pop(0)
    if fstack.count(noteVal) != len(fstack):
      if prenoteVal != noteVal:
        duration = int(ticker(estack[0]) - notebegin)       
        if (noteVal != 0) and (prenoteVal != 0):
          print (prenoteVal, noteVal, duration, end='')
          track.append(Message('note_on', note=prenoteVal, velocity=110, time=0))
          track.append(Message('note_off', note=prenoteVal, velocity=110, time=duration))
          notebegin = ticker(estack[0])
        prenoteVal = noteVal  

    if cv2.waitKey(25) & 0xFF == ord('q'):
      break

    elapsed += frametime

  else: 
    break

cap.release()
cv2.destroyAllWindows()
mid.save(midifile)
sys.exit()