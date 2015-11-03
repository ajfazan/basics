#!/bin/sh

if [ ${#} -ne 3 ]; then

  echo -e "\nUsage:"
  echo -e "\t$(basename ${0}) <YEAR> <JULIAN_DAY> <TARGET_DIR>"
  exit -1

fi

wget -c --recursive ftp://cddis.gsfc.nasa.gov/gps/products/ionex/${1}/${2}/igsg${2}"0.15i.Z" -P ${3}
