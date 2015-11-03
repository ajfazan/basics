#!/bin/sh

if [ ${#} -ne 1 ]; then

  echo -e "\nUsage:"
  echo -e "\t$(basename ${0}) <SUM_FILE>"
  exit -1

fi

if [ ! -f ${1} ]; then

  echo "${1} does not exist in filesystem"
  exit -1

fi

TARGET1="/tmp/"$(basename ${1})
TARGET2=${TARGET1}".geo"

# encode an ANSI file to UTF-8
iconv -f windows-1252 -t utf-8 ${1} > ${TARGET1}

grep 'Nome do Marco' ${TARGET1} | sed 's/ //g' | cut -d: -f2 > ${TARGET2}

N=$(grep -n ELIPSOIDAL ${TARGET1} | cut -d: -f1 | sed -n 2p)

EXP1="$((${N}+1)),$((${N}+2))p"

sed -n ${EXP1} ${TARGET1} | cut -d')' -f2 \
  | sed -r 's/ +/ /g ; s/^ +//g' | cut -d' ' -f'1,2,3,7' >> ${TARGET2}

EXP2="$((${N}+3))p"

sed -n ${EXP2} ${TARGET1} | cut -d')' -f2 \
  | sed -r 's/ +/ /g ; s/^ +//g' | cut -d' ' -f'1,3' >> ${TARGET2}

sed ':a;N;$!ba;s/\n/\t/g' ${TARGET2}

# :a       - create a label 'a'
# N        - append the next line to the pattern space
# $!       - if not the last line
# ba       - branch (go to) label 'a'
# s        - substitute
# /\n/     - regex for new line
# /<text>/ - with text "<text>"
# g        - global match (as many times as it can)

rm -f ${TARGET1} ${TARGET2}
