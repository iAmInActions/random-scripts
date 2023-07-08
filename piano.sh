#!/bin/bash

length=100

while true
do
  read -n1 key
  
  case $key in
  a)
    beep -l $length -f 261
    ;;
  w)
    beep -l $length -f 277
    ;;
  s)
    beep -l $length -f 293
    ;;
  e)
    beep -l $length -f 311
    ;;
  d)
    beep -l $length -f 329
    ;;
  f)
    beep -l $length -f 349
    ;;
  t)
    beep -l $length -f 369
    ;;
  g)
    beep -l $length -f 392
    ;;
  z)
    beep -l $length -f 415
    ;;
  y)
    beep -l $length -f 415
    ;;
  h)
    beep -l $length -f 440
    ;;
  u)
    beep -l $length -f 466
    ;;
  j)
    beep -l $length -f 493
    ;;
  k)
    beep -l $length -f 523
    ;;
  o)
    beep -l $length -f 554
    ;;
  l)
    beep -l $length -f 587
    ;;
  p)
    beep -l $length -f 622
    ;;
  *)
    sleep 0.$length
    ;;
esac
done
