#!/bin/sh

wget -c --recursive ftp://cddis.gsfc.nasa.gov/gps/products/$1/igs$1[0-6].{clk,sp3}.Z -P $2
