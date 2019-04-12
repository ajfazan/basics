#!/bin/sh

DIR=$(dirname ${1})

cd ${DIR}

RINEX=$(basename ${1})

teqc +meta ${RINEX} > .meta 2>/dev/null

dos2unix -q .meta

grep 'station name'  .meta | cut -d: -f2 | sed -r 's/^ +//g' > .station_name
grep 'receiver type' .meta | cut -d: -f2 | sed -r 's/^ +//g' > .receiver
grep 'antenna type'  .meta | cut -d: -f2 | sed -r 's/^ +//g' > .antenna

grep 'start date & time' .meta | cut -d: -f2- | sed -r 's/^ +//g ; s/ /\t/g' > .begin
grep 'final date & time' .meta | cut -d: -f2- | sed -r 's/^ +//g ; s/ /\t/g' > .end

META=$(cat .station_name)".meta"

paste .station_name .receiver .antenna .begin .end > ${META}

find -name ".*" -type f -delete
