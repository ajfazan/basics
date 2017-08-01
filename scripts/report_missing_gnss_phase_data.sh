#!/bin/sh

which teqc > /dev/null 2>&1

if [ ${?} -ne 0 ]; then

  echo "TEQC utility is required to run this tool"
  exit -1

fi

if [ ${#} -ne 1 ] || [ ! -f ${1} ]; then

  printf "\nUsage:\n\t%s <RINEX_OBS_FILE>\n" $(basename ${0})
  exit -1

fi

teqc +meta ${1} 2>/dev/null | dos2unix | grep 'file format' | grep -q RINEX

if [ ${?} -ne 0 ]; then

  echo "Input file format is not RINEX"
  exit -1

fi

SUM=${1}".sum"

teqc -O.sum . ${1} > ${SUM} 2>/dev/null

head -1 ${SUM} | sed -r 's/^ +//g' | sed -r 's/ +/\n/g' | egrep -n '^L' > .phase

L1=$(grep L1 .phase | cut -d: -f1)
L2=$(grep L2 .phase | cut -d: -f1)

L1=$(echo "${L1} + 1" | bc)
L2=$(echo "${L2} + 1" | bc)

while IFS=';' read SV L1 L2
do
  if [ $(echo "${L1} - ${L2}" | bc) -ne 0 ]; then

    echo -e "\tSV = ${SV} | # L1 = ${L1} | # L2 = ${L2}"

  fi
done <<< $(sed 1,2d ${SUM} | sed -r 's/^ +//g' \
                           | sed -r 's/ +/;/g' | cut -d';' -f"1,${L1}-${L2}")

rm -f ${SUM} .phase
