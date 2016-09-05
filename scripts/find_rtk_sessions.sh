#!/bin/sh

COUNT=0

for DIR in $(find ./ -name "*RTK" -type d); do

  cd ${DIR}

  STATION=$(basename ${DIR} | cut -d_ -f1)

  find ./ -iname "*.rw5" -type f > sessions.txt

  N=$(cat sessions.txt | wc -l)

  echo "- Found ${N} RTK session(s) based on reference station ${STATION}"

  if [ -z sessions.txt ]; then

    echo "Missing RTK file(s) for current RTK session"

  fi

  for SESSION in $(cat sessions.txt); do

    for BASE in $(grep 'base open' ${SESSION} | cut -d' ' -f4); do

      if [ $(find -name "${BASE}" -type f | wc -l) -eq 0 ]; then

        echo -e "\tBase GNSS raw data file '${BASE}' not found"

      else

        SUB=$(basename $(find -name "${BASE}" -type f -exec dirname {} \;))

        if [ "${SUB}" != "BASE" ]; then
          echo -e "\tBase GNSS raw data file is misplaced in directory ${SUB}"
        fi

      fi

    done

    for ROVER in $(grep 'rover open' ${SESSION} | cut -d' ' -f4); do

      if [ $(find -name "${ROVER}" -type f | wc -l) -eq 0 ]; then

        echo -e "\tRover GNSS raw data file '${ROVER}' not found"

      else

        SUB=$(basename $(find -name "${ROVER}" -type f -exec dirname {} \;))

        if [ "${SUB}" != "ROVER" ]; then
          echo -e "\Rover GNSS raw data file is misplaced in directory ${SUB}"
        fi

      fi

    done

  done

  COUNT=$((${COUNT}+1))

  rm -f sessions.txt

  cd - 1>/dev/null

done

echo -e "\nTOTAL: ${COUNT} RTK session(s) found"
