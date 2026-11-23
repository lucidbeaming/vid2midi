# vid2midi

Generate MIDI files from brightness levels in video.

**Project page:** [lucidbeaming.com/art/code](https://lucidbeaming.com/art/code)

vid2midi is a command-line tool that sonifies video: it watches one area of every frame and writes a MIDI note whenever that area gets brighter, darker or changes color. Load the `.mid` file into a DAW (Reaper, Ableton Live, Logic, Reason…) and any instrument plays in time with the picture.

It's the reverse of an audio visualizer. Instead of animating to finished music, you make the video first and then compose sounds that follow its timing and feel. Used plainly, it's also a timing track that marks scene changes and flashes when you're scoring a video.

## Requirements

- Python 3.9 or newer
- [OpenCV](https://opencv.org/) (`opencv-python`), [NumPy](https://numpy.org/), [Mido](https://mido.readthedocs.io/) and [tqdm](https://github.com/tqdm/tqdm), all installed from [`requirements.txt`](requirements.txt)
- Any video format OpenCV can read (MP4, MOV, AVI…)

## Install

```bash
git clone https://github.com/lucidbeaming/vid2midi.git
cd vid2midi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 vid2midi.py [options] video [output.mid]
```

Without `output.mid`, the file is written next to the video with a `.mid` extension. A preview window shows the sampled area as it's read; press `q` to stop early and save what's been read so far.

| Option | Values (default first) | What it does |
|---|---|---|
| `-s`, `--size` | `small`, `medium`, `large` | Size of the sampled square: 10 %, 20 % or 50 % of the frame's longer side |
| `-p`, `--position` | `center`, `topleft`, `bottomright` | Where the square sits |
| `-o`, `--octaves` | `1`, `3`, `7` | How many octaves of the chromatic scale the notes span |
| `-c`, `--colors` | `mono`, `all` | `mono`: brightness sets the note, velocity is fixed at 110. `all`: hue sets the note, brightness sets the velocity (75–127). |
| `--headless` | | No preview window, for SSH, servers or batch jobs |

Examples:

```bash
python3 vid2midi.py clip.mp4                       # brightness → notes in one octave, clip.mid
python3 vid2midi.py -o 3 -s large clip.mp4 cue.mid # a wider sample area and range
python3 vid2midi.py -c all -o 7 clip.mp4           # color → note, brightness → velocity
python3 vid2midi.py --headless -p topleft clip.mp4
```

### The notes

The measured value (brightness, or hue with `-c all`) is split into equal bands, one per semitone, centred on MIDI note 64 (E4):

| `-o` | Notes | Darkest (or red) → brightest (or purple) |
|---|---|---|
| `1` | 12 | 59 (B3) → 70 (A#4) |
| `3` | 36 | 47 (B2) → 82 (A#5) |
| `7` | 84 | 23 (B0) → 106 (A#7) |

Brighter areas give higher notes. With `-c all`, notes rise around the color wheel from red through yellow, green and blue to purple.

### In a DAW

The file has one track at 480 ticks per beat and no tempo event, so every DAW reads it at **120 BPM**. Set the project to 120 BPM before importing, or import with the file's tempo, and the notes line up with the video's timeline. Then route the track to any instrument.

## How it works

For each frame, [`vid2midi.py`](vid2midi.py):

1. cuts out the sample square and blurs it (15×15 Gaussian) so noise and fine texture don't trigger notes
2. converts it to HSV and averages the value channel (or the hue, with `-c all`)
3. maps that average to a note band
4. when the band changes, writes the previous note with its length and starts the next one

The MIDI file is written with [Mido](https://mido.readthedocs.io/) when the video ends. Note: note changes currently land four frames before the change in the picture ([#17](https://github.com/lucidbeaming/vid2midi/issues/17)).

## Related projects

- [p5-audio-visualizers](https://github.com/lucidbeaming/p5-audio-visualizers): the other direction, fullscreen visuals that react to sound
- [Camel](https://github.com/lucidbeaming/Camel): an Arduino drone synth
- [pi-synths](https://github.com/lucidbeaming/pi-synths): scripts for building music machines on Raspberry Pi

## License

[MIT](LICENSE). Releases before this change were published under GPL-3.0, and those copies keep that license.
