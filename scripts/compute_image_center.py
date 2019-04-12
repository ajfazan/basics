#!/usr/bin/env python

from osgeo  import gdal
import os, sys

def openImage( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    print "Unable to open image [%s]" % filename
    sys.exit( 1 )

  return handle

def computeCenter( img ):

  geo = img.GetGeoTransform()

  cx = geo[0] + 0.5 * geo[1] * img.RasterXSize
  cy = geo[3] + 0.5 * geo[5] * img.RasterYSize

  return ( cx, cy )

if __name__ == "__main__":

  argc = len( sys.argv ) - 1

  if argc != 1:
    print "Input argument must be a GDAL raster dataset"
    sys.exit( -1 )

  handle = openImage( sys.argv[1] )

  ( cx, cy ) = computeCenter( handle )

  print "%s, %f, %f" % ( os.path.basename( sys.argv[1] ), cx, cy )
