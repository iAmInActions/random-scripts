#!/bin/bash

TARGET="/path/to/destination"  # Specify the target directory where files should be moved

find . -type f -name "*.mp3" -print0 | while IFS= read -r -d $'\0' file; do
    artist=$(ffprobe -loglevel error -show_entries format_tags=artist -of default=noprint_wrappers=1:nokey=1 "$file")
    album=$(ffprobe -loglevel error -show_entries format_tags=album -of default=noprint_wrappers=1:nokey=1 "$file")
    track=$(ffprobe -loglevel error -show_entries format_tags=track -of default=noprint_wrappers=1:nokey=1 "$file")
    title=$(ffprobe -loglevel error -show_entries format_tags=title -of default=noprint_wrappers=1:nokey=1 "$file")
    filename=$(basename "$file")

    # Prepare destination directory path
    destination="$TARGET/$artist/$album"
    mkdir -p "$destination"

    # Move the file to the destination
    mv "$file" "$destination/$track"_"$title.mp3"
done
