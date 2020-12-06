#!/bin/sh

if [ ${#} -ne 1 ]; then

  printf "Usage:\n\t%s <GPS_WEEK>\n" $(basename ${0})
  exit 1

fi

GPS_WEEK=$(printf "%04d" ${1})

curl -u anonymous:ajfazan@gmail.com -O --ftp-ssl \
  ftp://gdc.cddis.eosdis.nasa.gov/gnss/products/${GPS_WEEK}/igs${GPS_WEEK}[0-6].sp3.Z

curl -u anonymous:ajfazan@gmail.com -O --ftp-ssl \
  ftp://gdc.cddis.eosdis.nasa.gov/glonass/products/${GPS_WEEK}/igl${GPS_WEEK}[0-6].sp3.Z
