#!/bin/sh

if [ ${#} -ne 3 ]; then

  printf "\nUsage:\n\t%s <MULTIBAND_IMAGE_FILE>" $(basename ${0})
  printf " <RED_BAND_NUMBER> <NIR_BAND_NUMBER>\n"
  exit -1

fi

TARGET=$(dirname ${1})"/"$(echo ${1} | sed 's/.tif/_NDVI.tif/')

gdal_calc.py -A ${1} --A_band ${2} -B ${1} --B_band ${3} --outfile=${TARGET} \
             --overwrite --type=Float32 --NoDataValue=-9999 \
             --calc="numpy.float64( ( B - 2 * ( B == 0 ) ) - A ) / ( ( B + ( B == 0 ) ) + A )"

gdal_edit.py -stats ${TARGET}
