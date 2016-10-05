#!/bin/sh

function help {

  TOOL=$(basename ${0})

  printf "\nUsage:\n\t%s <IMG_FILE> " ${TOOL}
  printf "<R_BAND_NUM> <G_BAND_NUM> <B_BAND_NUM> [<GRAY_IMG_FILE>]\n"
  printf "\nor\n\t%s" ${TOOL}
  printf " -r|--red <R_IMG_FILE>"
  printf " -g|--green <G_IMG_FILE>"
  printf " -b|--blue <B_IMG_FILE> <GRAY_IMG_FILE>\n"

  exit ${1}
}

function is_image_file {

  if [ ! -f ${1} ]; then

    echo "${1} must be an image file (GDAL supported format)"
    exit 1

  fi
}

function is_number {

  echo ${1} | egrep -q '^[+|-]?[0-9]+$'

  if [ ${?} -ne 0 ]; then

    echo "Parse error: Not a number"
    exit 2

  fi
}

OPTS=$(getopt -o "hr:g:b:" --long "help,red:,green:,blue:" -n ${0} -- "${@}")
eval set -- ${OPTS}

CHECK=0

while true; do

  case "${1}" in
    -h|--help)
      help 0
      ;;
    -r|--red)
      R_IMG_FILE=${2}
      CHECK=$(echo "${CHECK} + 1" | bc)
      shift 2
      ;;
    -g|--green)
      G_IMG_FILE=${2}
      CHECK=$(echo "${CHECK} + 1" | bc)
      shift 2
      ;;
    -b|--blue)
      B_IMG_FILE=${2}
      CHECK=$(echo "${CHECK} + 1" | bc)
      shift 2
      ;;
    --)
      shift
      break
      ;;
  esac

done

if [ ${CHECK} -eq 0 ]; then

  if [ ${#} -ne 4 ] && [ ${#} -ne 5 ]; then

    help 3

  fi

else

  if [ ${CHECK} -ne 3 ] || [ ${#} -ne 1 ]; then

    help 3

  fi

fi

if [ ${CHECK} -eq 0 ]; then

  is_image_file ${1}

  is_number ${2}
  is_number ${3}
  is_number ${4}

  if [ ${#} -ne 5 ]; then

    BASE=$(basename ${1})
    EXT=$(echo ${BASE} | cut -d. -f2)
    BASE=$(echo ${BASE} | cut -d. -f1)

    RESULT=$(dirname ${1})"/"${BASE}"_GRAYSCALE"${EXT}

  else

    RESULT=${5}

  fi

  gdal_calc.py -A ${1} --A_band ${2} \
               -B ${1} --B_band ${3} \
               -C ${1} --C_band ${4} \
               --outfile=${RESULT} --type=Byte --NoDataValue=0 \
               --calc="numpy.rint( 0.299 * A + 0.587 * B + 0.114 * C )" \
               > /dev/null 2>&1

else

  is_image_file ${R_IMG_FILE}
  is_image_file ${G_IMG_FILE}
  is_image_file ${B_IMG_FILE}

  gdal_calc.py -A ${R_IMG_FILE} \
               -B ${G_IMG_FILE} \
               -C ${B_IMG_FILE} \
               --outfile=${1} --type=Byte --NoDataValue=0 \
               --calc="numpy.rint( 0.299 * A + 0.587 * B + 0.114 * C )" \
               > /dev/null 2>&1

fi
