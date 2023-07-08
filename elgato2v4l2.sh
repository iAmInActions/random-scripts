#!/bin/bash

rmmod v4l2loopback
modprobe v4l2loopback

if [ "$1" = "hdmi" ]; then
    echo "HDMI mode selected."
    gchd -i hdmi -c rgb $2 $3 -of fifo /dev/elgatotmp.ts &
    sleep 6
    ffmpeg -i /dev/elgatotmp.ts -vcodec rawvideo -f v4l2 $(ls /dev/video* | tail -n1)
elif [ "$1" = "composite" ]; then
    echo "Composite mode selected."
    gchd -i composite -of fifo /dev/elgatotmp.ts &
    sleep 6
    ffmpeg -i /dev/elgatotmp.ts -f v4l2 $(ls /dev/video* | tail -n1)
elif [ "$1" = "component" ]; then
    echo "Component mode selected."
    gchd -i component -c rgb $2 $3 -of fifo /dev/elgatotmp.ts &
    sleep 6
    ffmpeg -i /dev/elgatotmp.ts -vcodec rawvideo -f v4l2 $(ls /dev/video* | tail -n1)
else
    echo "ERROR:"
    echo "Please specify a mode."
    echo "Usage: elgato2v4l2.sh [mode] <options>"
fi
