#!/bin/sh

wget -c --recursive ftp://cddis.gsfc.nasa.gov/glonass/products/$1/{emx$1[0-6].clk,igl$1[0-6].sp3}.Z -P $2

rename emx esx $2/cddis.gsfc.nasa.gov/glonass/products/$1/emx*
