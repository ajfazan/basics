#!/bin/sh

IFS=$'\n'

if [ ${#} -ne 1 ]; then

  echo -e "\nUsage:\n\t$(basename ${0}) <RINEX_DATA_DIR>"
  exit 0

fi

if [ ! -d ${1} ]; then

  echo "${1} is not a GNSS RINEX data directory"
  exit 1

fi

cd ${1}

STATION=$(basename ${1})

find \( -iname "*.*O" -or \
        -iname "*.*N" -or \
        -iname "*.*G" \) -type f > collection.dat

if [ $(cat collection.dat | wc -l) -ne 3 ]; then

  echo "WARNING: Check RINEX data files for point ${STATION}"

fi

if [ $(egrep -i 'O$' collection.dat | wc -l) -lt 1 ]; then

  echo "Missing GNSS observation data for point ${STATION}"

fi

if [ $(egrep -i 'N$' collection.dat | wc -l) -lt 1 ]; then

  echo "Missing GPS navigation data for point ${STATION}"

fi

if [ $(egrep -i 'G$' collection.dat | wc -l) -lt 1 ]; then

  echo "Missing GLONASS navigation data for point ${STATION}"

fi

rm -f collection.dat

cd - 1>/dev/null
