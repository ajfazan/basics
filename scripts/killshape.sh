#!/bin/sh

BASE=$(basename ${1})

if [ "$(echo ${BASE} | cut -d. -f2 | tr A-Z a-z)" != "shp" ]; then

  echo "${1} is not a SHAPEFILE"
  exit 1

fi

if [ -d ${1} ]; then

  rm -rf ${1}

elif [ -f ${1} ]; then

  BASE=$(echo ${BASE} | cut -d. -f1)

  DIR=$(dirname ${1})

  for EXT in $(echo "shp shx sbx sbn dbf prj qpj cpg"); do

    find ${DIR} -mindepth 1 -maxdepth 1 -iname ${BASE}"."${EXT} -type f -delete

  done

fi
