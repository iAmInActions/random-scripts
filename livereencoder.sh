echo "Live Re-encoder for low bandwidth"
echo "By Mueller Minki"
echo "Wrapper script by ScarlettPPC"

echo "Enter YouTube/TikTok/media link:"
read _link

echo "Enter quality (low, mid or high):"
read _quality


echo http://muellers-software.org/live-encode/video/mp4-h264.php?quality=${_quality}&url=${_link}
curl "http://muellers-software.org/live-encode/video/mp4-h264.php?quality=${_quality}&url=${_link}" | ffplay -


