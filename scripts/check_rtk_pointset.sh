#!/bin/sh

# check_rtk_pointset

function print_info {

  IFS=$'\n'

  for ITEM in $(sed 1d ${1} | cut -d';' -f${2} | sort -u); do

    printf "%s: %s\n" ${3} ${ITEM}

  done
}

# EQUIPE: 1
print_info ${1} 1 "EQUIPE"

# DESC: 1
print_info ${1} 3 "DESC"

# SIS_REF: 11
print_info ${1} 11 "SIS_REF"

# COD_EPSG: 12
print_info ${1} 12 "COD_EPSG"

# MET_POSIC: 13
print_info ${1} 13 "MET_POSIC"

# REC_ANT: 14
print_info ${1} 14 "REC_ANT"

# PONTO_BASE: 15
print_info ${1} 15 "PONTO_BASE"

# OBS_PROC: 16
print_info ${1} 16 "OBS_PROC"
