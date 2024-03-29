#!/usr/bin/env python3

import cv2
import numpy as np
import sys
import os.path
import argparse
from tqdm import tqdm
from collections import namedtuple
from mido import Message, MidiFile, MidiTrack, second2tick

parser = argparse.ArgumentParser(prog='vid2midi', description='Convert a section of a video file to MIDI notes based on color or brightness')
parser.add_argument('-s', '--size', default='small', type=str, choices=['small', 'medium', 'large'], help='size of the sample area')
parser.add_argument('-p', '--position', default='center', type=str, choices=['topleft', 'center', 'bottomright'], help='position of the sample area')
parser.add_argument('-o', '--octaves', default=1, type=int, choices=[1, 3, 7], help='octave range of resulting notes')
parser.add_argument('-c', '--colors', default='mono', type=str, choices=['mono', 'all'], help='color range to measure')
parser.add_argument('filename')
parser.add_argument('output')
parameters = parser.parse_args()
octaves = parameters.octaves
window_size = parameters.size
position = parameters.position
color_range = parameters.colors

if os.path.isfile(parameters.filename) is False:
    print("Input file '" + parameters.filename + "' does not exist")
    sys.exit()

if parameters.output:
    midifile = parameters.output
else:
    try:
        midifile = parameters.filename.split('.')[0] + '.mid'
    except KeyError:
        print("Bad input filename")
        sys.exit()

cap = cv2.VideoCapture(parameters.filename)
fps = cap.get(cv2.CAP_PROP_FPS)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
framecount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
window = {"small": .05, "medium": .1, "large": .25}
offset = {"topleft": .2, "center": 1, "bottomright": 1.8}

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

if cap.isOpened() is False:
    print("Error opening video stream or file")

fstack = [0]
estack = [0]
prenoteVal = 0
preVel = 0
notebegin = 0

cv2.namedWindow('sample')
cv2.moveWindow('sample', 250, 150)

for i in tqdm(range(framecount)):

    ret, frame = cap.read()
    if ret is True:
        if width > height:
            p = int(width * window[window_size])
        else:
            p = int(height * window[window_size])
        left = int((width / 2) * offset[position]) - p
        right = int((width / 2) * offset[position]) + p
        top = int((height / 2) * offset[position]) - p
        bottom = int((height / 2) * offset[position]) + p
        if (right > width) or (bottom > height):
            left = int(width) - p
            right = int(width)
            top = int(height) - p
            bottom = int(height)
        if (left < 0) or (top < 0):
            left = 0
            right = p
            top = 0
            bottom = p
        chunk = frame[top:bottom, left:right]
        blurchunk = cv2.GaussianBlur(chunk, (15, 15), 0)

        cv2.imshow('sample', blurchunk)

        hsv = cv2.cvtColor(blurchunk, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        if color_range == 'all':
            avg_hue = np.average(h.flatten())
            noteHue = int(np.interp(avg_hue, [0, 179], [0, 255]))
            avg = np.average(v.flatten())
            vel = int(np.interp(avg, [0, 255], [75, 127]))
            noteVal = detect_level(noteHue)
        else:
            avg = int(np.average(v.flatten()))
            vel = 110
            noteVal = detect_level(avg)

        fstack.append(noteVal)
        estack.append(elapsed)
        if (len(fstack) > 5):
            fstack.pop(0)
            estack.pop(0)
        if fstack.count(noteVal) != len(fstack):
            if prenoteVal != noteVal:
                duration = int(ticker(estack[0]) - notebegin)
                if (noteVal != 0) and (prenoteVal != 0) and noteVal is not None and prenoteVal is not None:
                    track.append(Message('note_on', note=prenoteVal, velocity=preVel, time=0))
                    track.append(Message('note_off', note=prenoteVal, velocity=preVel, time=duration))
                    notebegin = ticker(estack[0])
                prenoteVal = noteVal
                preVel = vel

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        elapsed += frametime

    else:
        break

duration = int(ticker(estack[0]) - notebegin)
track.append(Message('note_on', note=prenoteVal, velocity=preVel, time=0))
track.append(Message('note_off', note=prenoteVal, velocity=preVel, time=duration))

cap.release()
cv2.destroyAllWindows()
mid.save(midifile)
sys.exit()
