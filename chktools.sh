#!/bin/sh

BASE=$(echo ${1} | sed -r 's/^([^0-9]+)\.([^0-9]+)$/\1/')

TARGET=$(mktemp --tmpdir=$(dirname ${1}) --suffix=".csv" XXXXXXXXXXXXXXXX)

LIBDIR=$(dirname $(realpath ${0}))

if [ ${2} -eq 1 ]; then

  SQL="SELECT PONTO, ROUND( SQRT( POWER( SIGMA_LAT, 2.0 ) + POWER( SIGMA_LON, 2.0 ) ), 3 )"
  SQL="${SQL} AS S1_HOR, ROUND( SIGMA_HOR, 3 ) AS S2_HOR FROM gcp"
  SQL="${SQL} WHERE ABS( S1_HOR - S2_HOR ) > 1E-3"

  ogr2ogr -f CSV -lco SEPARATOR=SEMICOLON -sql "${SQL}" ${TARGET} ${1}

  sed -i "1d" ${TARGET}

  mv ${TARGET} "${BASE}.SIGMA_HOR_CALC.txt"

elif [ ${2} -eq 2 ]; then

  ogr2ogr -f CSV -lco SEPARATOR=SEMICOLON \
    -sql "SELECT PONTO, SIGMA_HOR FROM gcp WHERE SIGMA_HOR > ${3}" ${TARGET} ${1}

  sed -i "1d" ${TARGET}

  mv ${TARGET} "${BASE}.SIGMA_HOR.txt"

elif [ ${2} -eq 3 ]; then

  ogr2ogr -f CSV -lco SEPARATOR=SEMICOLON \
    -sql "SELECT PONTO, SIGMA_VERT FROM gcp WHERE SIGMA_VERT > ${3}" ${TARGET} ${1}

  sed -i "1d" ${TARGET}

  mv ${TARGET} "${BASE}.SIGMA_VERT.txt"

elif [ ${2} -eq 4 ]; then

  TMPDIR=$(dirname ${1})

  SUBSET=$(mktemp --tmpdir=${TMPDIR} --suffix=".dat" XXXXXXXXXXXXXXXX)

  cut -d';' -f ${3} ${1} | sed 's/,/./g ; s/"//g ; s/;/|/g' > ${SUBSET}

  LAT=$(mktemp --tmpdir=${TMPDIR} --suffix=".lat.dat" XXXXXXXXXXXXXXXX)
  LON=$(mktemp --tmpdir=${TMPDIR} --suffix=".lon.dat" XXXXXXXXXXXXXXXX)

  cut -d'|' -f2 ${SUBSET} > ${LAT}
  cut -d'|' -f3 ${SUBSET} > ${LON}

  BP="([0-9]{1,3})([^0-9]+)([0-9]{1,2})([^0-9]+)([0-9]{1,2})(\.[0-9]*)?"

  if [ $(egrep -c '(N|S)$' ${LAT}) -gt 0 ]; then

    sed -i -r "s/^${BP}( *)(N|S)$/\1d\3'\5\6\8/g" ${LAT}

  else

    sed -i -r 's/^ +//g ; s/ +$//g' ${LAT}

    sed -i -r "s/^([^0-9]?)${BP}$/\2d\4'\6\7\1/g" ${LAT}

    sed -i -r "s/^(.+)(\-)$/\1S/g" ${LAT}

  fi

  if [ $(egrep -c '(E|W)$' ${LON}) -gt 0 ]; then

    sed -i -r "s/^${BP}( *)(E|W)$/\1d\3'\5\6\8/g" ${LON}

  else

    sed -i -r 's/^ +//g ; s/ +$//g' ${LON}

    sed -i -r "s/^([^0-9]?)${BP}$/\2d\4'\6\7\1/g" ${LON}

    sed -i -r "s/^(.+)(\-)$/\1W/g" ${LON}

  fi

  PLAN=$(mktemp --tmpdir=${TMPDIR} --suffix=".dat" XXXXXXXXXXXXXXXX)

  cut -d'|' -f'1,4-5' ${SUBSET} > ${PLAN}

  paste -d ' ' ${LAT} ${LON} | cs2cs -f "%.4f" EPSG:4674 EPSG:${4} | \
    sed -r 's/(\t| )+/|/g' | cut -d'|' -f1-2 > ${SUBSET}

  if [ ${#} -eq 5 ]; then
    TOLERANCE=${5}
  else
    TOLERANCE=0.0005
  fi

  paste -d '|' ${PLAN} ${SUBSET} | awk -v FS='|' -v THS=${TOLERANCE} -f "${LIBDIR}/coords.awk"

  rm -f ${LAT} ${LON} ${PLAN} ${SUBSET} ${TARGET}

elif [ ${2} -eq 5 ]; then

  for FIELD in $(cat "${LIBDIR}/distinct.txt"); do

    TARGET=$(mktemp --tmpdir=$(dirname ${1}) --suffix=".csv" XXXXXXXX)

    ogr2ogr -f CSV -sql "SELECT DISTINCT ${FIELD} FROM gcp" ${TARGET} ${1}

    sed -i '1d ; s/"//g' ${TARGET}

    mv ${TARGET} "${BASE}.${FIELD}.dat"

  done

elif [ ${2} -eq 6 ]; then

  cut -d';' -f ${3} ${1} | awk -v FS=';' -v THS=0.0001 -f "${LIBDIR}/heights.awk" > ${TARGET}

  mv ${TARGET} "${BASE}.HEIGHTS.dat"

fi

rm -f ${TARGET}
