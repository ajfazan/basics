#!/bin/sh

if [ ${#} -ne 3 ]; then

  echo -e "Usage:\n\t$(basename ${0}) <IMAGE_FILE> <NODATA_VALUE> <OUT_DIR>"
  exit 0

fi


if [ ! -f ${1} ]; then

  echo "First input argument must be an image file (GDAL supported format)"
  exit 1

fi

echo ${2} | egrep -q '^[+|-]?[0-9]+$'

if [ ${?} -ne 0 ]; then

  echo "Second argument must be a valid number"
  exit 1

fi

if [ ! -d ${3} ]; then

  echo "Third input argument must be a directory"
  exit 1

fi

LOGICAL=$(printf "%s( %s( A!=%s, B!=%s ), C!=%s )" \
                  "numpy.logical_or" "numpy.logical_or" ${2} ${2} ${2})

TEMP="${TMP}/orto_mask_"$(shuf -i 0-1000 -n 1)".tif"

gdal_calc.py -A ${1} --A_band=1 \
             -B ${1} --B_band=2 \
             -C ${1} --C_band=3 \
             --calc="127*${LOGICAL}" --NoDataValue=255 --type=Byte \
             --overwrite --outfile=${TEMP} 1>/dev/null 2>&1

TARGET=${3}"/"$(basename ${1} | cut -d. -f1)".shp"

gdal_polygonize.py -q ${TEMP} -f "ESRI Shapefile" ${TARGET}

rm -f ${TEMP}
