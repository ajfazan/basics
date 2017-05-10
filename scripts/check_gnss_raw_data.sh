#!/bin/sh

if [ ${#} -ne 1 ]; then

  echo -e "\nUsage:\n\t$(basename ${0}) <GNSS_RAW_DATA_DIR>"
  exit 0

fi

if [ ! -d ${1} ]; then

  echo "${1} is not a GNSS raw data directory"
  exit 1

fi

cd ${1}

STATION=$(basename ${1})

if [ $(ls *.* | wc -l) -ne 1 ]; then

  echo "WARNING: Check GNSS raw data for point ${STATION}"

fi

cd - 1>/dev/null
