#!/bin/sh

if [ ${#} -ne 3 ]; then

  printf "\nUsage:\n\t%s <MULTIBAND_IMAGE_FILE>" $(basename ${0})
  printf " <RED_BAND_NUMBER> <NIR_BAND_NUMBER>\n"
  exit -1

fi

BASE=$(basename ${1} | cut -d. -f1)

RED_BAND="/tmp/"${BASE}"_RED.tif"
NIR_BAND="/tmp/"${BASE}"_NIR.tif"

gdal_calc.py -A ${1} --A_band ${2} --calc="A + ( A == 0 )" \
             --outfile=${RED_BAND} --type="Float32" 2>&1 1>/dev/null

gdal_calc.py -A ${1} --A_band ${3} --calc="A + ( A == 0 )" \
             --outfile=${NIR_BAND} --type="Float32" 2>&1 1>/dev/null

TARGET=$(dirname ${1})"/"${BASE}"_NDVI.tif"

gdal_calc.py -A ${RED_BAND} -B ${NIR_BAND} --outfile=${TARGET} \
             --overwrite --type=Float32 --NoDataValue=-9999 \
             --calc="numpy.float64( B - A ) / ( B + A )" 2>&1 1>/dev/null

gdal_edit.py -stats ${TARGET}

rm -f ${RED_BAND} ${NIR_BAND}
