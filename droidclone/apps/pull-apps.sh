#!/bin/bash
txtfile=$(cat list.txt)

echo "Android App pull"
echo "(c) 2023 mueller_minki; Licensed under GPL3"

mkdir out >/dev/null

for i in $txtfile
do
  echo "Getting location of $i..."
  apkpath=$(adb shell pm path "$i" | grep -oP "^package:\K.*")
  echo "Localising finished."
  mkdir "out/$i"
  for p in $apkpath
  do
    echo "Pulling $p"
    adb pull "$p" "out/$i"
    echo "Pulling finished."
  done
done

