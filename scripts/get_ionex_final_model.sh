#!/bin/sh

wget -c --recursive ftp://cddis.gsfc.nasa.gov/gps/products/ionex/$1/$2/igsg$2"0.15i.Z" -P $3
