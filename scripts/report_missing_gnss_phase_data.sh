#!/bin/sh

which teqc > /dev/null 2>&1

if [ ${?} -ne 0 ]; then

  echo "TEQC utility is required to run this tool"
  exit -1

fi

if [ ${#} -ne 2 ] || [ ! -f ${1} ]; then

  printf "\nUsage:\n\t%s <RINEX_OBS_FILE> <THS>\n" $(basename ${0})
  exit -1

fi

teqc +meta ${1} 2>/dev/null | dos2unix | grep 'file format' | grep -q RINEX

if [ ${?} -ne 0 ]; then

  echo "Input file format is not RINEX"
  exit -1

fi

SUM=${1}".sum"

teqc -O.sum . ${1} > ${SUM} 2>/dev/null

dos2unix -q ${SUM}

head -1 ${SUM} | sed -r 's/^ +//g' | sed -r 's/ +/\n/g' | egrep -n '^L' > .phase

L1=$(grep L1 .phase | cut -d: -f1)
L2=$(grep L2 .phase | cut -d: -f1)
L5=$(grep L5 .phase | cut -d: -f1)

L1=$(echo "${L1} + 1" | bc)
L2=$(echo "${L2} + 1" | bc)

SYSTEMS="G R"

if [ "${L5}" != "" ]; then

  L5=$(echo "${L5} + 1" | bc)
  SYSTEMS=" E"

fi

if [ "$(locale -f)" == "pt_BR" ]; then

  LC_ALL="en_US.UTF-8"

fi


for KEY in $(echo ${SYSTEMS}); do

  FIELDS="1,${L1}"

  if [ ${KEY} != "E" ]; then

    FIELDS=${FIELDS}",${L2}"
    F2_ID="L2"

  else

    FIELDS=${FIELDS}",${L5}"
    F2_ID="L5"

  fi

  while IFS=';' read SV F1 F2
  do

    RATIO=$(echo "${F2}/${F1}" | bc -l)

    if [ $(echo "${RATIO} < ${2}" | bc) -eq 1 ]; then

      printf "SV = %s | # L1 = %5d | # %s = %5d" ${SV} ${F1} ${F2_ID} ${F2}
      printf " | %s/L1 = %.3lf\n" ${F2_ID} ${RATIO}

    fi

  done <<< $(sed 1,2d ${SUM} | sed -r 's/^ +//g' | sed -r 's/ +/;/g' \
                             | egrep "^"${KEY} | cut -d';' -f${FIELDS})

done

rm -f ${SUM} .phase
