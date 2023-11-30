#!/bin/bash

cd /home/gregor/Pictures/Wallpapers/

if [[ $(date +%u) == 3 ]];
then
  echo "Its wednesday my dudes!";
  xfconf-query --channel xfce4-desktop --property /backdrop/screen0/monitorDSI1/workspace0/last-image --set $(pwd)/default-frog.png
else
  echo "Not a wednesday :("
  xfconf-query --channel xfce4-desktop --property /backdrop/screen0/monitorDSI1/workspace0/last-image --set $(pwd)/default-wallpaper.png
fi
