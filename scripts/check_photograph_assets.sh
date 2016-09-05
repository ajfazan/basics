#!/bin/sh

if [ $(find ./ -mindepth 1 -maxdepth 1 -type d | wc -l) -ne ${1} ]; then

  echo "Number of expected points mismatch"
  exit 1

fi

for DIR in $(find ./ -mindepth 1 -maxdepth 1 -type d); do

  if [ $(find $DIR -iname "*.jp*g" -type f | wc -l) -lt 5 ]; then

    echo "Number of photographs for $(basename $DIR) is less than expected"

  fi

done
