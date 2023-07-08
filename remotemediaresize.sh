#!/bin/bash
# Remote Multimedia playback script for users with low bandwidth internet.
# Written by Minki in 2023. Feel free to share and modify.
# Client Dependencies: ffmpeg (with ffplay), ssh, dialog
# Server Dependencies: sshd, ffmpeg, yt-dlp

# PROCESSING SETTINGS:
# Video stream parameters
vStream="-vf scale=320:240 -r 8 -f matroska -c:v wmv1 -acodec libmp3lame -ac 1 -ar 44100"
# Audio stream parameters
aStream="-f mp3 -acodec libmp3lame -ac 1 -ar 44100"
# SSH Server login details (user@server.top)
sshLogin="mueller@muellers-software.org"
# Youtube-dl installation path
ytDlCmd="yt-dlp"

# Initial Values:
searchTerm=""
inputUrl=""
vBit="24"
aBit="24"

# FUNCTIONS:

setInputType () {
  inputType=$(dialog --backtitle "Remote Media Resize Service" --menu "Input type?" 14 45 25 \
    1 "URL" \
    2 "YouTube URL" \
    3 "YouTube Search" \
    4 "Exit" \
    3>&1 1>&2 2>&3 
  )
}

setMode () {
  mode=$(dialog --backtitle "Remote Media Resize Service" --menu "Playback type?" 14 45 25 \
    1 "Play Audio" \
    2 "Play Video" \
    3 "Download Audio" \
    4 "Download Video" \
    5 "Exit" \
    3>&1 1>&2 2>&3 
  )
}

setAudioBitrate () {
  aBit=$(dialog --backtitle "Remote Media Resize Service" \
    --inputbox "Enter Audio Bitrate (in kbps) " 8 60 $aBit \
    3>&1 1>&2 2>&3 
  )k
}

setVideoBitrate () {
  vBit=$(dialog --backtitle "Remote Media Resize Service" \
    --inputbox "Enter Video Bitrate (in kbps) " 8 60 $vBit \
    3>&1 1>&2 2>&3 
  )k
}

setInputUrl () {
  inputUrl=$(dialog --backtitle "Remote Media Resize Service" \
    --inputbox "Enter URL " 8 60 \
    3>&1 1>&2 2>&3 
  )
}

setSearchTerm () {
  searchTerm=$(dialog --backtitle "Remote Media Resize Service" \
    --inputbox "Enter search term " 8 60 \
    3>&1 1>&2 2>&3 
  )
}

setSaveName () {
  saveName=$(dialog --backtitle "Remote Media Resize Service" \
    --inputbox "Save file as? " 8 60 \
    3>&1 1>&2 2>&3 
  )
}

setQuery () {
  query=$(dialog --backtitle "Remote Media Resize Service" \
    --inputbox "Enter a search term " 8 60 \
    3>&1 1>&2 2>&3 
  )
}

setFfArguments () {
  case $mode in
  1)
    setAudioBitrate
    ffArguments="$aStream -b:a $aBit "
    ;;
  2)
    setAudioBitrate
    setVideoBitrate
    ffArguments="$vStream -b:a $aBit -b:v $vBit"
    ;;
  3)
    setAudioBitrate
    ffArguments="$aStream -b:a $aBit "
    ;;
  4)
    setAudioBitrate
    setVideoBitrate
    ffArguments="$vStream -b:a $aBit -b:v $vBit"
    ;;
  5)
    normalExit
    ;;
  *)
    abnormalExit
    ;;
  esac
}

normalExit () {
  echo "Interrupted by user."
  exit 0
}

abnormalExit () {
  echo "Exiting abnormally..."
  exit 127
}

# MAIN LOOP:

# Intro screen:
echo '  ___               _       __  __        _ _      ___        _        
 | _ \___ _ __  ___| |_ ___|  \/  |___ __| (_)__ _| _ \___ __(_)______ 
 |   / -_) "  \/ _ \  _/ -_) |\/| / -_) _` | / _` |   / -_|_-< |_ / -_)
 |_|_\___|_|_|_\___/\__\___|_|  |_\___\__,_|_\__,_|_|_\___/__/_/__\___|
 Written by mueller_minki in 2023. Feel free to share and modify!'
sleep 1
clear
echo 'IMPORTANT! If you do not have SSH keys set up, you will have to enter your password on every rempote operation. If you are using the search feature, this might get annoying.'
sleep 1

setInputType # Query the user for what type of input they want to provide
case $inputType in
1) # URL
  setInputUrl
  urlInputType="URL"
  setMode
  setFfArguments
  ;;
2) # YouTube URL
  setInputUrl
  urlInputType="YT"
  setMode
  setFfArguments
  ;;
3) # YouTube Search
  setSearchTerm
  urlInputType="YT"
  setMode
  setFfArguments
  ;;
4)
  normalExit
  ;;
*)
  abnormalExit
  ;;
esac

if [ $mode -gt 2 ]
then # Mode 3 or 4 aka Download
  setSaveName
  if [ $urlInputType == "URL" ]
  then
    ssh $sshLogin "ffmpeg -re -i \"$inputUrl\" $ffArguments pipe:1" > $saveName
  elif [ $urlInputType == "YT" ]
  then
    if [ $inputType == "3" ]
    then
      ssh $sshLogin "ffmpeg -re -i \$($ytDlCmd -q -f b -g \"ytsearch1:$inputUrl\" ) $ffArguments pipe:1" > $saveName
    else
      ssh $sshLogin "ffmpeg -re -i \$($ytDlCmd -q -f b -g \"$inputUrl\" ) $ffArguments pipe:1" > $saveName
    fi
  else
    abnormalExit
  fi
else # Mode 1 or 2 aka Play
  if [ $urlInputType == "URL" ]
  then
    ssh $sshLogin "ffmpeg -re -i \"$inputUrl\" $ffArguments pipe:1" | ffplay -hide_banner -loglevel error -stats -
  elif [ $urlInputType == "YT" ]
  then
    if [ $inputType == "3" ]
    then
      ssh $sshLogin "ffmpeg -re -i \$($ytDlCmd -q -f b -g ytsearch1:\"$searchTerm\" ) $ffArguments pipe:1" | ffplay -hide_banner -loglevel error -stats -
    else
      ssh $sshLogin "ffmpeg -re -i \$($ytDlCmd -q -f b -g \"$inputUrl\" ) $ffArguments pipe:1" | ffplay -hide_banner -loglevel error -stats -
    fi
  else
    abnormalExit
  fi  
fi



