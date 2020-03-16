#!/usr/bin/env python3

from osgeo import gdal

import numpy as np
import math
import sys
import os

gdal.UseExceptions()

def Usage( code ):

  print( "Usage:" )
  print( "\t%s <IMG1> <IMG2>" % os.path.basename( sys.argv[0] ) )
  sys.exit( code )

def OpenImage( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    print( "Unable to open image %s" % filename )
    sys.exit( 1 )

  return handle

def DisplayMetadata( himg ):

  n = himg.RasterCount

  print( "Band count: %s" % n )

  for band in range( 1, n + 1 ):

    channel = himg.GetRasterBand( band )

    if channel is None:
      continue

    print( "NODATA VALUE = ", channel.GetNoDataValue() )
    print( "MINIMUM = ", channel.GetMinimum() )
    print( "MAXIMUM = ", channel.GetMaximum() )
    print( "SCALE = ", channel.GetScale() )
    print( "UNIT TYPE = ", channel.GetUnitType() )

def ComputeCorr( img1, img2 ):

  n = img1.RasterCount

  if n != img2.RasterCount:
    print( "Band count mismatch" )
    return None

  for band in range( 1, n + 1 ):

    x = np.array( img1.GetRasterBand( band ).ReadAsArray() )
    y = np.array( img2.GetRasterBand( band ).ReadAsArray() )

    k = x.size

    if k == y.size:

      x = ( x - x.mean() ) / k
      y = ( y - y.mean() ) / k

      s_xx = np.sum( x * x, dtype = np.float64 )
      s_yy = np.sum( y * y, dtype = np.float64 )
      s_xy = np.sum( x * y, dtype = np.float64 )

      try:

        corr = s_xy / ( math.sqrt( s_xx ) * math.sqrt( s_yy ) )
        print( "Correlation coefficient [%d|%d]: %f" % ( band, band, corr ) )

      except( ValueError, e ):

        print( "Unable to compute correlation: %s" % e )
        pass

def main( img1, img2 ):

  h1 = OpenImage( img1 )
  h2 = OpenImage( img2 )

  # DisplayMetadata( h1 )
  # DisplayMetadata( h2 )

  ComputeCorr( h1, h2 )

if __name__ == "__main__":

  if len( sys.argv ) != 3:
    Usage( 1 )

  main( sys.argv[1], sys.argv[2] )
