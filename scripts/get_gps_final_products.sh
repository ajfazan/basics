#!/bin/sh

if [ ${#} -ne 2 ]; then

  echo -e "\nUsage:"
  echo -e "\t$(basename ${0}) <GPS_WEEK> <TARGET_DIR>"
  exit -1

fi

wget -c --recursive ftp://cddis.gsfc.nasa.gov/gps/products/${1}/igs${1}[0-6].{clk,sp3}.Z -P ${2}
