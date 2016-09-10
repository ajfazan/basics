#!/bin/sh

if [ ${#} -ne 3 ]; then

  echo -e "Usage:\n\t$(basename ${0}) <IMAGE_FILE> <NODATA_VALUE> <OUT_DIR>"
  exit 0

fi


if [ ! -f ${1} ]; then

  echo "First input argument must be an image file"
  exit 1

fi

if [ $(echo ${2} | egrep -q '^[+|-]?[0-9]+$') -ne 0 ];

  echo "Second argument must be a valid number"
  exit 1

fi

if [ ! -d ${3} ]; then

  echo "Third input argument must be a directory"
  exit 1

fi

LOGICAL=$(printf "%s( %s( %s( A==%s, B==%s ), C==%s ), D==%s )" \
                 "numpy.logical_and" \
                 "numpy.logical_and" \
                 "numpy.logical_and" ${2} ${2} ${2} ${2})

TMP="/tmp/tmp_$(shuf -i 0-1000 -n 1).tif"

TARGET=${3}/$(basename {1} | cut -d. -f1)".shp"

gdal_calc.py -A ${1} --A_band=1 \
             -B ${1} --B_band=2 \
             -C ${1} --C_band=3 \
             -D ${1} --D_band=4 --calc="127*${LOGICAL}" --NoDataValue=255 \
             --type=Byte --outfile=${TARGET} 1>/dev/null 2>&1

gdal_polygonize -q ${TMP} -f "ESRI Shapefile" ${TARGET}

rm -f ${TMP}
