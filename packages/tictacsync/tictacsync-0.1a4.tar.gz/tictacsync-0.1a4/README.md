# tictacsync

## Warning: this is at pre-alpha stage

Unfinished sloppy code ahead, but should run without errors. Some functionalities are still missing. Don't run the code without parental supervision. Suggestions and enquiries are welcome via the [lists hosted on sourcehut](https://sr.ht/~proflutz/TicTacSync/lists).

## Description

`tictacsync` is a python script to sync audio and video files shot
with [dual system sound](https://www.learnlightandsound.com/blog/2017/2/23/how-to-record-sound-for-video-dual-systemsync-sound)  using a specific hardware timecode generator
called [Tic Tac Sync](https://tictacsync.org). The timecode is named YaLTC for *yet
another longitudinal time code* and should be recorded on a scratch
track on each device for the syncing to be performed, later in _postprod_ before editing.

## Status

`tictacsync`  scans for audio video files and displays their starting time and then merges overlapping audio and video recordings. Multicam syncing with one stereo audio recorder has been tested (spring 2023, [see demo](https://youtu.be/pklTSTi7cqs)). Multi audio recorders coming soon... 


## Installation

First, you need running [ffmpeg](https://windowsloop.com/install-ffmpeg-windows-10/) and [sox](http://sox.sourceforge.net/) installations _accessible through your `PATH` system environment variable_.
Then pip install the program:


    pip install tictacsync


This should install python dependencies _and_ the `tictacsync` command.
## Usage

Download some sample files [here](https://tictacsync.org/sampleFiles.zip), unzip and run 

    tictacsync sampleFiles
The resulting synced videos will be in a subfolder `tictacsynced`. For a very verbose output add the `-v` flag:

    tictacsync -v sampleFiles

When the argument is an unique media file (not a directory) two zoomable plots will be produced for diagnostic purpose (close the plotting window for the 2nd one) and the decoded starting time will be output to stdin:

    tictacsync sampleFiles/canon24fps01.MOV

Typical first plot produced :

![word](https://mamot.fr/system/media_attachments/files/110/279/794/002/305/269/original/0198908c6eb5c592.png)

Typical second plot produced (note the 34 [FSK](https://en.wikipedia.org/wiki/Frequency-shift_keying) encoded bits `0010111101001111100110000110010000`):
![slicing](https://mamot.fr/system/media_attachments/files/110/279/794/021/372/766/original/6ec62bb417115f52.png)

and the `stdout` output:

```
recording started at 2022-03-01 19:57:28.796803+00:00
true sample rate 44099.353 Hz
first sync at 53060 samples
```


<!-- To run some tests, from top level `git cloned` dir:

    cd tictacsync ; python -m pytest
 Yes, the coverage is low. -->