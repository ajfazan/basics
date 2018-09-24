#!/bin/sh

# ${1} TIFF image filename
# ${2} Chip ID
# ${3} X coordinate of image chip center
# ${4} Y coordinate of image chip center
# ${5} Image chip x size
# ${6} Image chip y size

CHIP_FILENAME=${2}".tif"

if [ ! -e ${CHIP_FILENAME} ]; then

  gdalinfo ${1} | grep 'Pixel Size' | sed -r 's/ +//g' > tmp.gsd
  GSD=$(cut -d'=' -f2 tmp.gsd | sed 's/(//g ; s/)//g' | cut -d',' -f1)
  rm -f tmp.gsd

  ULX=$(echo "${3} - ${GSD} * ${5} / 2.0" | bc -l)
  ULY=$(echo "${4} + ${GSD} * ${6} / 2.0" | bc -l)

  LRX=$(echo "${ULX} + ${GSD} * ${5}" | bc -l)
  LRY=$(echo "${ULY} - ${GSD} * ${6}" | bc -l)

  gdal_translate -q -stats -r bilinear -co COMPRESS=LZW \
    -projwin ${ULX} ${ULY} ${LRX} ${LRY} ${1} ${CHIP_FILENAME}

fi
