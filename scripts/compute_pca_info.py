#!/usr/bin/env python

from osgeo import gdal

import numpy as np

import math, os, sys

gdal.UseExceptions()

def openImage( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    print "Unable to open image %s" % filename
    sys.exit( 1 )

  return handle

def computePCA( img ):

  n = img.RasterCount

  corr = np.zeros( ( n, n ), dtype = np.float64 )

  bands = []

  nodata = []
  pixels = []

  for k in range( 1, n + 1 ):

    band = img.GetRasterBand( k )
    nodata.append( band.GetNoDataValue() )
    array = np.array( band.ReadAsArray(), dtype = np.float64 )

    logical = ( array != nodata[-1] )

    array[array == nodata[-1]] = 0.0
    count = logical.sum()
    assert( count != 0.0 )

    mean = array.sum() / count
    array[logical] -= mean
    array /= ( count - 1.0 )

    bands.append( array )

    pixels.append( count )

  assert( np.std( pixels ) == 0.0 );
  assert( np.std( nodata ) == 0.0 );

  for i in range( n ):
    x = bands[i]
    corr[i,i] = np.sum( x * x, dtype = np.float64 )
    for j in range( i + 1, n ):

      y = bands[j]
      corr[j,j] = np.sum( y * y )
      corr[i,j] = np.sum( x * y )

  for i in range( n ):
    v = corr[i,i]
    corr[i,i] = 1.0
    for j in range( i + 1, n ):
      corr[i,j] /= v
      corr[j,i] = corr[i,j]

  w, v = np.linalg.eigh( corr )

  return w, v, corr


def main( argv ):

  h = openImage( argv[1] )

  w, v, corr = computePCA( h )

  w = abs( w )

  n = w.size
  s = w.sum()

  for k in range( n ):
    print "PC%d Percent Info: %f" % ( k + 1, w[n-k-1] / s )

  return 0

if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print "Usage:"
    print "\t%s <IMAGE>" % os.path.basename( sys.argv[0] )
    sys.exit( -1 )

  main( sys.argv )
