#!/bin/sh

if [ ${#} -ne 2 ]; then

  echo -e "\nUsage:\n\t$(basename ${0}) <POINTS_COUNT> <IMAGES_COUNT>"
  exit 0

fi

FILE=${TMP}"/point_list_"$(shuf -i 0-1000 -n 1)".tmp"

find ./ -mindepth 1 -maxdepth 1 -type d -exec basename {} \; > ${FILE}

if [ $(cat ${FILE} | wc -l) -ne ${1} ]; then

  echo "WARNING: Number of expected points mismatch"

  sed -i -r 's/^[0-9]+[A-Z]+//g' ${FILE}

  for POINT in $(seq ${1}); do

    PATTERN=$(printf "%02d" ${POINT})

    grep -q "^"${PATTERN} ${FILE}

    if [ ${?} -eq 1 ]; then

      echo -e " - Point ${POINT} is missing"

    fi

  done

  rm -f ${FILE}

  exit 1

fi

for DIR in $(find ./ -mindepth 1 -maxdepth 1 -type d); do

  COUNT=$(find ${DIR} -iname "*.jp*g" -type f | wc -l)

  if [ ${COUNT} -lt ${2} ]; then

    echo -n "WARNING: "
    echo -n "Number of photographs for $(basename ${DIR}) is less than expected"
    echo " >> (${COUNT} < 5)"

  fi

done

rm -f ${FILE}
