#!/bin/sh

BASE=$(basename ${1} | cut -d. -f1)

PREFIX=${PREFIX}

R_BAND=${PREFIX}"_R.tif"

gdal_calc.py -A ${1} --A_band ${2} --calc="A / 255.0" --type=Float32 \
                     --outfile=${R_BAND} --overwrite 2>&1 1>/dev/null

G_BAND=${PREFIX}"_G.tif"

gdal_calc.py -A ${1} --A_band ${3} --calc="A / 255.0" --type=Float32 \
                     --outfile=${G_BAND} --overwrite 2>&1 1>/dev/null

B_BAND=${PREFIX}"_B.tif"

gdal_calc.py -A ${1} --A_band ${4} --calc="A / 255.0" --type=Float32 \
                     --outfile=${B_BAND} --overwrite 2>&1 1>/dev/null

I_BAND=${PREFIX}"_I.tif"

gdal_calc.py -A ${R_BAND} -B ${G_BAND} -C ${B_BAND} --type=Float32 --overwrite \
             --outfile=${I_BAND} --calc="0.299 * A + 0.587 * B + 0.114 * C" 2>&1 1>/dev/null

S_BAND=${PREFIX}"_S.tif"

gdal_calc.py -A ${R_BAND} -B ${G_BAND} -C ${B_BAND} -D ${I_BAND} --type=Float32 --overwrite \
             --outfile=${S_BAND} --calc="1.0 - numpy.minimum( numpy.minimum( A, B ), C ) / D" 2>&1 1>/dev/null

S_MASK=${PREFIX}"_S_MASK.tif"

gdal_calc.py -A ${I_BAND} -B ${S_BAND} --calc="127 * ( ( A - B ) < 0.0 )" \
             --overwrite --outfile=${S_MASK} --type=Byte --NoDataValue=255 2>&1 1>/dev/null

gdal_sieve.py -st 25 ${S_MASK}

#TARGET=${5}"/"${BASE}"_smask.shp"
TARGET=${5}"/"${BASE}"_smask.tif"

mv ${S_MASK} ${TARGET}

# gdal_polygonize.py -q ${S_MASK} -f "ESRI Shapefile" ${TARGET}

rm -f ${R_BAND} ${G_BAND} ${B_BAND} ${I_BAND} ${S_BAND} ${S_MASK}
