#!/usr/bin/env python3

import time
import cv2
import numpy as np
import sys
import argparse
from tqdm import tqdm
from collections import namedtuple
from mido import Message, MidiFile, MidiTrack, second2tick

class SizeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 10 < values < 500:
            raise argparse.ArgumentError(self, "sample size must be between 10 and 500")
        setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser(prog='vid2midi', description='Convert a section of a midifile to MIDI notes based on average brightness')
parser.add_argument('-s', '--size', default='small', type=str, choices=['small', 'medium', 'large'], help='size of the sample area')
parser.add_argument('-o', '--octaves', default=1, type=int, choices=[1, 3, 7], help='octave range of resulting notes')
parser.add_argument('filename')
parameters = parser.parse_args()
octaves = parameters.octaves
window_size = parameters.size

try:
    midifile = parameters.filename.split('.')[0] + '.mid'
except KeyError:
    print("Bad input filename")
    sys.exit()

cap = cv2.VideoCapture(parameters.filename)
fps = cap.get(cv2.CAP_PROP_FPS)
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
framecount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
window = {"small": .05, "medium": .1, "large": .25}

mid = MidiFile()
mid.ticks_per_beat = 480
mid.tempo = 500000
track = MidiTrack()
mid.tracks.append(track)

_blevels = []
j = 0
brange_step = int(256 / (octaves * 12))
bval_lower = int(64 - ((octaves * 12) / 2))
BLevel = namedtuple("BLevel", ['brange', 'bval'])

for octave in range(1, octaves + 1):
    for i in range(1, 13):
        j += 1
        if (octave == octaves) and (i == 12):
            end_step = 255
        else:
            end_step = j * brange_step
        _blevels.append(BLevel(brange=range(((j - 1) * brange_step), end_step), bval=j + bval_lower))

def detect_level(h_val):
    h_val = int(h_val)
    for blevel in _blevels:
        if h_val in blevel.brange:
            return blevel.bval

def ticker(t_val):
    ticks = int(second2tick(t_val, mid.ticks_per_beat, mid.tempo))
    return ticks


frametime = 1 / fps
ticktime = ticker(frametime)
elapsed = 0

if (cap.isOpened() is False):
    print("Error opening video stream or file")

fstack = [0]
estack = [0]
prenoteVal = 0
notebegin = 0

cv2.namedWindow('sample')        # Create a named window
cv2.moveWindow('sample', 250, 150)

for i in tqdm(range(framecount)):
    ret, frame = cap.read()
    if ret is True:
        if w > h:
            p = int(w * window[window_size])
        else:
            p = int(h * window[window_size])
        left = int(w / 2) - p
        right = int(w / 2) + p
        top = int(h / 2) - p
        bottom = int(h / 2) + p
        chunk = frame[left:right, top:bottom]
        blurchunk = cv2.GaussianBlur(chunk, (15, 15), 0)

        cv2.imshow('sample', blurchunk)

        hsv = cv2.cvtColor(blurchunk, cv2.COLOR_BGR2HSV)
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