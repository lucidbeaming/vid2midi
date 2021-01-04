# vid2midi
 Generates a midi file based on color or brightness levels in a video

Requires [OpenCV](https://opencv.org/), [Mido](https://mido.readthedocs.io/en/latest/) and [tqdm](https://github.com/tqdm/tqdm).

### Usage
vid2midi [-h] [-s {small,medium,large}] [-o {1,3,7}] [-c {mono,all}] filename

  -h, --help, show this help message and exit
  -s, --size {small,medium,large}, size of the sample area
  -o, --octaves {1,3,7}, octave range of resulting notes
  -c, --colors {mono,all}, color range to measure
 
#### Notes
 It works by grabbing a square in the center of the video file, blurring it, and averaging the hue or brightness values of the contained pixels. Iterating each frame of the movie file, it looks for a value that is consistent for at least 5 frames. If it is, a note is generated corresponding to 1, 3, or 7 octaves of the chromatic scale. Brighter areas or purple produce higher notes.
 
#### Why is this useful?
When soundtracking videos in a Digital Audio Workstation such as Reaper, Ableton, or Reason, it is useful to have a timing track that corresponds to the video to match the timing of scene changes. As a creative tool it is the reverse of visualizing audio. Instead of generating audio reactive animation, this allows for creating a video first, without a soundtrack. Then you can make music or sounds that match the tempo and feel of the visuals. 
