#!/bin/sh

if [ ${#} -ne 3 ]; then

  echo -e "\nUsage:"
  echo -e "\t$(basename ${0}) <YEAR> <JULIAN_DAY> <TARGET_DIR>"
  exit -1

fi

IONEX=$(printf "igsg%s0.%si.Z" ${2} $(echo "${1} - 2000" | bc))

wget -c --recursive ftp://cddis.gsfc.nasa.gov/gps/products/ionex/${1}/${2}/${IONEX} -P ${3}
