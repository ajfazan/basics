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

BASE=$(basename ${1} | sed -r 's/^(.*)\.(.*)$/\1/')

MASK="${TMP}/${BASE}.mask.tif"

gdal_calc.py -A ${1} --calc="( A >= 0.0 )" --NoDataValue=0 --type=Byte --format=GTiff \
                     --overwrite --quiet --outfile=${MASK}

TARGET="${2}/${BASE}.shp"

gdal_polygonize.py -q ${MASK} -f "ESRI Shapefile" ${TARGET}

SQL=$(printf "ALTER TABLE %s ADD COLUMN SOURCE VARCHAR(64)" ${BASE})

ogrinfo -q ${TARGET} -sql "${SQL}"

SQL=$(printf "UPDATE '%s' SET SOURCE = '%s'" ${BASE} $(basename ${1}))

ogrinfo -q ${TARGET} -dialect SQLite -sql "${SQL}"

rm -f ${MASK}
