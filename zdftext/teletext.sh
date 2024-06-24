#!/bin/bash
clear
echo "ZDF TeletextViewer für Linux"
echo "(c) 2024 mueller_minki"
echo "Freigegeben zum Bearbeiten und Teilen."
sleep 2

page=100

while [[ $(tput lines) -ne 26 ]] || [[ $(tput cols) -ne 41 ]]
do
  clear
  echo "Resize your terminal to 41x26"
  sleep 0.2
done

while true
do
  clear
  curl "https://teletext.zdf.de/teletext/zdf/seiten/klassisch/$page.html" | python3 teletext2ansi.py
  read -n 3 page
  sleep 1
done
