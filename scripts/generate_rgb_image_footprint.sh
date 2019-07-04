#!/bin/sh

function help {

  printf "\nUsage:\n\t$(basename ${0}) [ -h | -f ]"
  printf " <IMAGE_FILE> <NODATA_VALUE> <OUT_DIR>\n"
  exit ${1}
}

while getopts "h" OPT; do
  case ${OPT} in
    h) help 0;;
  esac
done

shift $((${OPTIND} - 1))

if [ ${#} -ne 3 ]; then

  help 1

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

BASE=$(basename ${1} | sed -r 's/^(.*)\.(.*)$/\1/')

MASK="${TMP}/${BASE}.mask.tif"

LOGICAL=$(printf "numpy.logical_or( A == %d, B == %d )" ${2} ${2})
LOGICAL=$(printf "numpy.logical_not( numpy.logical_or( %s, C == %d ) )" "${LOGICAL}" ${2})

gdal_calc.py -A ${1} --A_band=1 \
             -B ${1} --B_band=2 \
             -C ${1} --C_band=3 \
             --calc="${LOGICAL}" \
             --NoDataValue=0 --type=Byte --format=GTiff \
             --overwrite --quiet --outfile=${MASK}

if [ ${?} -eq 0 ]; then

  TARGET="${3}/${BASE}.shp"

  gdal_polygonize.py -q ${MASK} -f "ESRI Shapefile" ${TARGET}

  SQL=$(printf "ALTER TABLE %s RENAME COLUMN DN TO ID" ${BASE})

  ogrinfo -q ${TARGET} -sql "${SQL}"

  SQL=$(printf "ALTER TABLE %s ADD COLUMN SOURCE VARCHAR(64)" ${BASE})

  ogrinfo -q ${TARGET} -sql "${SQL}"

  SQL=$(printf "UPDATE '%s' SET SOURCE = '%s'" ${BASE} $(basename ${1}))

  ogrinfo -q ${TARGET} -dialect SQLite -sql "${SQL}"

fi

rm -f ${MASK}
