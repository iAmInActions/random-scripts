#!/bin/bash
date -s "$(curl -I 'http://muellers-software.org/thispagegivesa404error' 2>/dev/null | grep -i '^date:' | sed 's/^[Dd]ate: //g' | tr -d ,)"
