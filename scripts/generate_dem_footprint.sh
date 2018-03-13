#!/bin/sh

if [ ${#} -ne 2 ]; then

  echo -e "Usage:\n\t$(basename ${0}) <IMAGE_FILE> <OUT_DIR>"
  exit 0

fi

if [ ! -f ${1} ]; then

  echo "First input argument must be a DEM file (GDAL supported format)"
  exit 1

fi

if [ ! -d ${2} ]; then

  echo "Second input argument must be a directory"
  exit 1

fi

TEMP="${TMP}/dem_mask_"$(shuf -i 0-1000 -n 1)".tif"

gdal_calc.py -A ${1} --calc="127*( A >= 0.0 )" --NoDataValue=255 --type=Byte \
                     --overwrite --outfile=${TEMP} 1>/dev/null 2>&1

TARGET=${2}"/"$(basename ${1} | cut -d. -f1)".shp"

if [ -e ${TARGET} ]; then

  killshape.sh ${TARGET}

fi

gdal_polygonize.py -q ${TEMP} -f "ESRI Shapefile" ${TARGET}

LAYER=$(basename ${TARGET} .shp)

SQL=$(printf "ALTER TABLE %s ADD COLUMN SOURCE VARCHAR(64)" ${LAYER})

ogrinfo -q ${TARGET} -sql "${SQL}"

SQL=$(printf "UPDATE '%s' SET SOURCE = '%s'" ${LAYER} $(basename ${1}))

ogrinfo -q ${TARGET} -dialect SQLite -sql "${SQL}"

rm -f ${TEMP}
