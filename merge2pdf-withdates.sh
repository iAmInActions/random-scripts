#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <parent_directory>"
    exit 1
fi

parent_directory="$1"
olddir=$(pwd)

# Check if the parent directory exists
if [ ! -d "$parent_directory" ]; then
    echo "Error: Parent directory does not exist."
    exit 1
fi

# Loop through subdirectories
for subdir in "$parent_directory"/*/; do

    pdffiles=""
    subdirname=$(basename "$subdir")
    image_path="$subdir/index.pdf"
    
    # Generate the image
    convert -size 600x870 xc:white -font "Liberation-Sans" -pointsize 32 -fill black -gravity north -annotate +0+100 "Dokumente vom $subdirname" "$image_path"
    
    echo "Generated fontpage for $subdirname"

    for xournal in $(find \"$subdir\" | grep xopp)
    do
      echo "Converting $xournal to pdf..."
      xournalpp -p "$xournal".pdf "$xournal" >/dev/null
    done
    
    echo "Merging PDF files from $subdir..."
    pdffiles="$(find "$subdir" ! -name 'index.pdf' | grep pdf)"
    pdftk "$subdir"index.pdf $pdffiles cat output "$1/$subdirname".pdf
    
done

echo "Merging all PDFs into one large file..."
subdirpdfs="$(ls $1 | grep '\.pdf')"

cd $1
pdftk $subdirpdfs cat output abgabe.pdf
cd $olddir

