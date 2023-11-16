#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <directory_path> <output_file_name>"
    exit 1
fi

directory_path="$1"
output_file_name="$2"
data_file="$output_file_name.data"

# Create the .data file
cat "$directory_path"/* > "$data_file"

# Create the .info file
info_file="$output_file_name.info"
echo 'loadPackage({' > "$info_file"
echo '    "files": [' >> "$info_file"

# Iterate over files in the directory and gather information
index=0
start=0

for file in "$directory_path"/*; do
    filename=$(basename "$file")
    size=$(wc -c < "$file")
    end=$((start + size))

    # Write file information to the .info file
    echo '        {' >> "$info_file"
    echo '            "filename": "'"$filename"'",' >> "$info_file"
    echo '            "start": '"$start"',' >> "$info_file"
    echo '            "end": '"$end"',' >> "$info_file"
    echo '            "audio": 0' >> "$info_file"
    echo '        },' >> "$info_file"

    ((index++))
    start=$end
done

# Remove the trailing comma from the last entry
sed -i '$s/,$//' "$info_file"

echo '    ],' >> "$info_file"
echo '    "remote_package_size": '"$(wc -c < "$data_file")"',' >> "$info_file"
echo '    "package_uuid": "'$(uuidgen)'"' >> "$info_file"
echo '})' >> "$info_file"

echo "Script completed successfully!"

