#!/bin/bash
cd out
find -name '*mp3' -exec mp3gain -r -k {} \;
