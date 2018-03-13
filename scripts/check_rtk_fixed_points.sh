#!/bin/sh

if [ ! -f ${1} ]; then

  echo "Input argument must be a CSV file"
  exit 1

fi

COUNT=0

for PDOP in $(sed 1d ${1} | grep FIXED | cut -d';' -f17 | sed 's/,/./g'); do

  if [ $(echo "${PDOP} <= 5.0" | bc -l) -eq 1 ]; then

    let COUNT++

  fi

done

echo "'${1}' has ${COUNT} fixed points"
