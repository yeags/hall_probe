# Hall Probe / CMM Integration
![Image](images/overview.jpg)
## Intro

This project is designed to integrate a Senis 3-axis hall sensor with a Zeiss Accura CMM.
Instead of using a start-and-stop method of mapping a magnetic field, this system will map on-the-fly along a given path.  The advantages to this method is a major time savings for large mapping areas while only sacrificing a relatively small amount of positional accuracy.

## Equipment and Hardware

### Zeiss Accura CMM
Placeholder description...
### National Instruments cDAQ
Placeholder description...
### Senis Electronic Control Box
Placeholder description...
### Field Sensitive Volume (FSV) Tool
Placeholder description...
### Orthogonal Cube
Placeholder description...

## Software

The entire project is written in Python.  So far this is still a work in progress and code may break or change in the meantime.  GUI started out as an empty proof of concept and is slowly being modified to contain actual functionality.  Currently only the probe qualification routines are integrated and working within the graphical interface.

Third party libraries utilized are:

* numpy
* matplotlib
* Pillow
* nidaqmx