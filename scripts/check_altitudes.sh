#!/bin/sh

if [ ${#} -ne 3 ] || [ ! -f ${1} ]; then

  printf "\nUsage:\n\t%s" $(basename ${0})
  printf " <CSV_FILE> <FIELD_SEPARATOR> <FIELD_LIST>\n"
  exit 0

fi

if [ "$(basename ${1} | cut -d. -f2 | tr a-z A-Z)" != "CSV" ]; then

  echo "ERROR: First argument must be a CSV file!"
  exit 1

fi

while IFS=${2} read ID h N H
do

  if [ $(echo "(${h} - ${N}) == ${H}" | bc) -ne 1 ]; then

    echo "INFO: Altitudes of point '${ID}' in file '${1}' mismatch"

  fi

done <<< $(cut -d${2} -f${3} ${1} | sed 1d)
