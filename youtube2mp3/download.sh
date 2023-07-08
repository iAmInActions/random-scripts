#!/bin/bash
# Reads songs from songs.txt formatted in the following way:
# Artist_-_Song_name
# The song names may not contain the " character.
# Made by mueller_minki in 2023.

while read i; do
  if [[ ! -e "./out/$i.mp4" ]]
  then
    yt-dlp -f 'ba' -x --audio-format mp3 --output "./out/$i.mp3" "ytsearch1:${i//_/ }"
    sleep 1
  else
    echo "$i was already downloaded."
  fi
done <songs.txt
