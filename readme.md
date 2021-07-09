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

## Software

The entire project is written in Python.  Third party libraries utilized are:

```
numpy
matplotlib
Pillow
nidaqmx
```