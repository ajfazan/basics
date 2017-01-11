#!/bin/sh

if [ ${#} -ne 5 ] || [ ! -f ${1} ]; then

  printf "\nUsage:\n\t%s" $(basename ${0})
  printf " <CSV_FILE> <FIELD_SEPARATOR> <FIELD_LIST> <SIGMA_H> <SIGMA_V>\n"
  exit 0

fi

if [ "$(basename ${1} | cut -d. -f2 | tr a-z A-Z)" != "CSV" ]; then

  echo "ERROR: First argument must be a CSV file!"
  exit 1

fi

echo ${4} | egrep -q '^[+]?[0-9]+\.[0-9]+$'

if [ ${?} -ne 0 ]; then

  echo "ERROR: <SIGMA_H> must be a positive number"
  exit 1

fi

echo ${5} | egrep -q '^[+]?[0-9]+\.[0-9]+$'

if [ ${?} -ne 0 ]; then

  echo "ERROR: <SIGMA_V> must be a positive number"
  exit 1

fi

while IFS=${2} read ID SIGMA_H SIGMA_V
do

  if [ $(echo "${SIGMA_H} > ${4}" | bc) -eq 1 ] \
  || [ $(echo "${SIGMA_V} > ${5}" | bc) -eq 1 ]; then

    echo "INFO: Point ID=${ID} is less precise than required!"

  fi

done <<< $(cut -d${2} -f${3} ${1} | sed 1d)
