#!/bin/sh

if [ ${#} -ne 1 ]; then

  echo -e "\nUsage:\n\t$(basename ${0}) <RINEX_DATA_DIR>"
  exit 0

fi

if [ ! -d ${1} ]; then

  echo "${1} is not a GNSS RINEX reference data directory"
  exit 1

fi

cd ${1}

STATION=$(basename ${1})

find -mindepth 1 -maxdepth 1 -type d > sessions.dat

if [ ! -s sessions.dat ]; then

  echo "." > sessions.dat

fi

for DIR in $(cat sessions.dat); do

  find \( -iname "*.pdf" -or \
          -iname "*.*O" -or \
          -iname "*.*N" -or \
          -iname "*.*G" \) -type f > collection.dat

  COUNT=$(egrep -i '[O|N|G]$' collection.dat | wc -l)

  if [ $(echo "${COUNT} % 3" | bc) -ne 0 ]; then

    echo "WARNING: Check GNSS RINEX data files for reference station ${STATION}"

  fi

  if [ $(egrep -i 'O$' collection.dat | wc -l) -lt 1 ]; then

    echo "Missing GNSS observation data for reference station ${STATION}"

  fi

  if [ $(egrep -i 'N$' collection.dat | wc -l) -lt 1 ]; then

    echo "Missing GPS navigation data for reference station ${STATION}"

  fi

  if [ $(egrep -i 'G$' collection.dat | wc -l) -lt 1 ]; then

    echo "Missing GLONASS navigation data for reference station ${STATION}"

  fi

  if [ $(egrep -i 'pdf$' collection.dat | wc -l) -lt 1 ]; then

    echo "Missing PPP processing report for reference station ${STATION}"

  fi

  rm -f collection.dat

done

rm -f sessions.dat

cd - 1>/dev/null
