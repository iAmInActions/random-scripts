#!/bin/bash

export PLAYER="ffplay"
export PLAYERARGS="-nodisp -hide_banner -loglevel error"

while true
do

if [ -z "$prchan" ]
then
  prdisp="Playback stopped."
else
  prdisp="Now playing: $prchan"
fi

channel=$(dialog --backtitle "$prdisp" --menu "Choose a station:" 18 45 25 \
  1 "80s80s" \
  2 "80s80s In the mix" \
  3 "100,5" \
  4 "100,5 In the mix" \
  5 "1Live" \
  6 "WDR 2" \
  7 "Antenne AC" \
  8 "WDR Cosmo" \
  9 "Radio21" \
  10 "Radio Digby" \
  11 "Exit" \
  3>&1 1>&2 2>&3 
)

clear
kill $PLAYERID

case $channel in
1)
  prchan="80s80s"
  "$PLAYER" "https://streams.80s80s.de/web/mp3-192/" $PLAYERARGS &
  PLAYERID=$!
  ;;
2)
  prchan="80s80s In the mix"
  "$PLAYER" "https://regiocast.streamabc.net/regc-80s80smix8012507-mp3-192-3015055" $PLAYERARGS &
  PLAYERID=$!
  ;;
3)
  prchan="100,5"
  "$PLAYER" "https://stream.dashitradio.de/dashitradio/mp3-128/stream.mp3" $PLAYERARGS &
  PLAYERID=$!
  ;;
4)
  prchan="100,5 In the mix"
  "$PLAYER" "https://stream.dashitradio.de/in_the_mix/mp3-128" $PLAYERARGS &
  PLAYERID=$!
  ;;
5)
  prchan="1Live"
  "$PLAYER" "http://wdr-1live-live.icecast.wdr.de/wdr/1live/live/mp3/128/stream.mp3" $PLAYERARGS &
  PLAYERID=$!
  ;;
6)
  prchan="WDR 2"
  "$PLAYER" "http://wdr-wdr2-aachenundregion.icecast.wdr.de/wdr/wdr2/aachenundregion/mp3/128/stream.mp3" $PLAYERARGS &
  PLAYERID=$!
  ;;
7)
  prchan="Antenne AC"
  "$PLAYER" "http://mp3.antenneac.c.nmdn.net/ps-antenneac/livestream.mp3" $PLAYERARGS &
  PLAYERID=$!
  ;;
8)
  prchan="WDR Cosmo"
  "$PLAYER" "http://wdr-cosmo-live.icecast.wdr.de/wdr/cosmo/live/mp3/128/stream.mp3" $PLAYERARGS &
  PLAYERID=$!
  ;;
9)
  prchan="Radio21"
  "$PLAYER" "https://radio21.streamabc.net/radio21-hannover-mp3-192-3735655" $PLAYERARGS &
  PLAYERID=$!
  ;;
10)
  prchan="Radio Digby"
  "$PLAYER" "http://ourdns.zone:8000/radiodigby.mp3" $PLAYERARGS &
  PLAYERID=$!
  ;;
11)
  killall $PLAYER
  echo "Exiting..."
  exit 0
  ;;
*)
  echo "Not a valid channel."
  exit 1
  ;;
esac

done
