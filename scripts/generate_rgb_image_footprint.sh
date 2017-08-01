#!/bin/sh

function help {

  printf "\nUsage:\n\t$(basename ${0}) [ -h | -p ]"
  printf " <IMAGE_FILE> <NODATA_VALUE> <OUT_DIR>\n"
  exit ${1}
}

PARTIAL=0

while getopts "ph" OPT; do
  case ${OPT} in
    p) PARTIAL=1;;
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

RAND=$(shuf -i 0-1000 -n 1)

R_LOGICAL_BAND="${TMP}/_R_logical_${RAND}.tif"
G_LOGICAL_BAND="${TMP}/_G_logical_${RAND}.tif"
B_LOGICAL_BAND="${TMP}/_B_logical_${RAND}.tif"

gdal_calc.py -A ${1} --A_band=1 --calc="A!=${2}" --NoDataValue=-1 --type=Byte \
                                --outfile=${R_LOGICAL_BAND} > /dev/null 2>&1

gdal_calc.py -A ${1} --A_band=2 --calc="A!=${2}" --NoDataValue=-1 --type=Byte \
                                --outfile=${G_LOGICAL_BAND} > /dev/null 2>&1

gdal_calc.py -A ${1} --A_band=3 --calc="A!=${2}" --NoDataValue=-1 --type=Byte \
                                --outfile=${B_LOGICAL_BAND} > /dev/null 2>&1

TEMP1="${TMP}/image_mask_${RAND}.tif"

if [ ${PARTIAL} -eq 1 ]; then

  gdal_calc.py -A ${R_LOGICAL_BAND} \
               -B ${G_LOGICAL_BAND} \
               -C ${B_LOGICAL_BAND} \
               --calc="127 * ( ( A + B + C ) == 3 )" --NoDataValue=255 \
               --type=Byte --overwrite --outfile=${TEMP1} 1>/dev/null 2>&1

else

  gdal_calc.py -A ${R_LOGICAL_BAND} \
               -B ${G_LOGICAL_BAND} \
               -C ${B_LOGICAL_BAND} \
               --calc="127 * ( ( A + B + C ) != 0 )" --NoDataValue=255 \
               --type=Byte --overwrite --outfile=${TEMP1} 1>/dev/null 2>&1

fi

TEMP2=$(echo ${TEMP1} | sed 's/tif/shp/')

gdal_polygonize.py -q ${TEMP1} -f "ESRI Shapefile" ${TEMP2}

TARGET=${3}"/"$(basename ${1} | cut -d. -f1)".shp"

ogr2ogr ${TARGET} ${TEMP2} -f "ESRI Shapefile" -where "DN=127"

rm -f ${R_LOGICAL_BAND} ${G_LOGICAL_BAND} ${B_LOGICAL_BAND} ${TEMP1}

killshape.sh ${TEMP2}
