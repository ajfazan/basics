#!/bin/sh

function create_temp_filename {

  TEMP="${TMP}/downsample"$(shuf -i 0-1000 -n 1)".tif"

  while [ -e ${TEMP} ]; do

    TEMP="${TMP}/downsample"$(shuf -i 0-1000 -n 1)".tif"

  done

  echo ${TEMP} | tee -a .tmp.local
}

GSD=${2}
INPUT=""
PARENT=${1}
STEPS=0

while [ $(echo "${GSD} < ${3}" | bc) -ne 0 ]; do

  GSD=$(echo "${GSD} * 2.0" | bc)

  INPUT=$(create_temp_filename)

  gdalwarp -q -multi -r average -tr ${GSD} ${GSD} ${PARENT} ${INPUT}

  PARENT=${INPUT}

  STEPS=$(echo "${STEPS} + 1" | bc)

done

if [ ${STEPS} -gt 0 ]; then

  tail -1 .tmp.local | xargs -I{} cp {} ${4}/$(basename ${1})

fi

cat .tmp.local | xargs rm -f
rm -f .tmp.local
