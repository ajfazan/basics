#!/bin/sh

if [ ${#} -ne 2 ]; then

  printf "Usage:\n\t%s <YEAR> <GPS_WEEK>\n" $(basename ${0})
  exit 1

fi

# wget -c ftp://cddis.gsfc.nasa.gov/glonass/products/${2}/emx${2}[0-6].sp3.Z

# wget -c ftp://cddis.gsfc.nasa.gov/pub/gps/products/mgex/${2}/com${2}[0-6].sp3.Z

wget -c ftp://ftp.unibe.ch/aiub/CODE/${1}/COD${2}[0-6].ION.Z
