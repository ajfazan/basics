#!/bin/sh

function compute_temporary_filename {

  TEMP="${TMP}/"$(shuf -i 0-1000000 -n 1)

  while [ -e ${TEMP} ]; do

    TEMP="${TMP}/"$(shuf -i 0-1000000 -n 1)

  done

  echo ${TEMP}
}

teqc +qc ${1} > qc.report 2>&1

FILE=$(basename ${1})

BASE=$(dirname ${1})"/"${FILE%.*}"."$(echo ${FILE##*.} | cut -c1-2)

G_FILE=${BASE}"G"
N_FILE=${BASE}"N"

read X Y Z <<< $(grep 'antenna WGS 84 (xyz)' qc.report \
                | cut -d: -f2 | sed -r 's/^ +//g ; s/ \(m\)//g')

TEMP=$(compute_temporary_filename)

teqc +O.px ${X} ${Y} ${Z} ${1} > ${TEMP} 2>/dev/null && mv ${TEMP} ${1}

N_TEMP=$(compute_temporary_filename)
G_TEMP=$(compute_temporary_filename)

teqc ${N_FILE} > ${N_TEMP} && mv ${N_TEMP} ${N_FILE}
teqc ${G_FILE} > ${G_TEMP} && mv ${G_TEMP} ${G_FILE}

rm -f qc.report
