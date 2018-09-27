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

  sigma = np.zeros( ( n, n ), dtype = np.float64 )

  bands = []; pixels = []

  for k in range( 1, n + 1 ):

    band = img.GetRasterBand( k )
    array = np.array( band.ReadAsArray(), dtype = np.float64 )

    null = band.GetNoDataValue()
    logical = ( array != null )
    count = logical.sum()
    assert( count != 0.0 )

    array[array == null] = 0.0
    mean = array.sum() / count
    array[logical] -= mean
    array /= ( count - 1.0 )

    bands.append( array ); pixels.append( count )

  pixels = np.unique( pixels )
  assert( pixels.size == 1 )

  for i in range( n ):
    x = bands[i]
    sigma[i,i] = np.sum( x * x, dtype = np.float64 )
    for j in range( i + 1, n ):
      y = bands[j]
      sigma[i,j] = np.sum( x * y, dtype = np.float64 )

  corr = np.identify( n )

  for i in range( n ):
    cxx = sigma[i,i]
    for j in range( i + 1, n ):
      cyy = sigma[j,j]
      corr[i,j] = sigma[i,j] / math.sqrt( cxx * cyy )
      corr[j,i] = corr[i,j]

  w, v = np.linalg.eigh( corr )

  return w, v, corr

def main( argv ):

  h = openImage( argv[1] )

  w, v, corr = computePCA( h )

  w /= w.sum()

  k = 0

  for p in w[::-1]:
    print "PC%d Percent Info: %f" % ( k += 1, p )

  return 0

if __name__ == "__main__":

  if len( sys.argv ) != 2:
    print "Usage:"
    print "\t%s <IMAGE>" % os.path.basename( sys.argv[0] )
    sys.exit( -1 )

  main( sys.argv )
