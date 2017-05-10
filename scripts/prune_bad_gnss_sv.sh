#!/bin/sh

which teqc > /dev/null
if [ ${?} -ne 0 ]; then

  echo "TEQC is required to run this tool"
  return -1

fi

if [ ${#} -ne 2 ] || [ ! -f ${1} ]; then

  printf "\nUsage:\n\t%s <TEQC_SUM_FILE> <TARGET_DIR>\n" $(basename ${0})
  exit -1

fi

DIR=$(dirname ${1})
BASE=$(basename ${1})

BASE=$(echo ${BASE} | cut -d. -f1)"."$(echo ${BASE} | cut -d. -f2 | cut -c1-2)

O_FILE=$(find ${DIR} -iname ${BASE}"O" -type f)
G_FILE=$(find ${DIR} -iname ${BASE}"N" -type f)
R_FILE=$(find ${DIR} -iname ${BASE}"G" -type f)

G=$(grep 'NAVSTAR GPS unhealthy SV' ${1} | \
    cut -d: -f2 | sed -r 's/^ +//; s/ +$//' | sed -r 's/ +/,/g')

R=$(grep 'GLONASS unhealthy SV' ${1} | \
    cut -d: -f2 | sed -r 's/^ +//; s/ +$//' | sed -r 's/ +/,/g')

TARGET=${2}/${DIR}
mkdir -p ${TARGET}

OPTIONS="-R3,4"

if [ "${G}" != "" ]; then
  OPTIONS="${OPTIONS} -G${G}"
fi

if [ "${R}" != "" ]; then
  OPTIONS="${OPTIONS} -R${R}"
fi

if [ "${G_FILE}" != "" ]; then

  RESULT=${TARGET}/$(basename ${G_FILE})

  if [ "${G}" != "" ]; then
    teqc -G${G} ${G_FILE} > ${RESULT} 2>/dev/null
  else
    teqc ${G_FILE} > ${RESULT} 2>/dev/null
  fi

  # sed -i '4,5d' ${RESULT}

fi

if [ "${R_FILE}" != "" ]; then

  RESULT=${TARGET}/$(basename ${R_FILE})

  if [ "${R}" != "" ]; then
    R=$(echo "3,4,$R" | sed 's/,/\n/g' | sort -n -u | sed ':a;N;$!ba;s/\n/,/g')
  else
    R="3,4"
  fi

  teqc -R${R} ${R_FILE} > ${RESULT} 2>/dev/null

  # sed -i '4,5d' ${RESULT}

fi

RESULT=${TARGET}/$(basename ${O_FILE})

teqc ${OPTIONS} ${O_FILE} > ${RESULT} 2>/dev/null

# sed -i -r '/^teqc edited/d ; 4,5d' ${RESULT}
