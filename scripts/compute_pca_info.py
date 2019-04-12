#!/usr/bin/env python

from osgeo import gdal, osr
import numpy as np
import math, os, sys

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

    array[array == null] = np.nan
    mean = np.nansum( array ) / count
    array[logical] -= mean

    bands.append( array ); pixels.append( count )

  pixels = np.unique( pixels )
  assert( pixels.size == 1 )

  df = pixels[0] - 1.0
  m = 0

  for i in range( n ):
    x = bands[i]
    sigma[i,i] = np.nansum( x * x, dtype = np.float64 ) / df
    m += 1
    for j in range( i + 1, n ):
      y = bands[j]
      sigma[i,j] = np.nansum( x * y, dtype = np.float64 ) / df
      sigma[j,i] = sigma[i,j]
      m += 2

  assert( m == ( n * n ) )

  corr = np.identity( n )

  for i in range( n ):
    cxx = sigma[i,i]
    for j in range( i + 1, n ):
      cyy = sigma[j,j]
      corr[i,j] = sigma[i,j] / math.sqrt( cxx * cyy )
      corr[j,i] = corr[i,j]

  w, v = np.linalg.eigh( corr )

  print "\nCORRELATION =\n"
  print corr

  return w, v, corr

def transformImage( img, v, args ):

  n = img.RasterCount

  ( cols, rows ) = ( img.RasterXSize, img.RasterYSize )

  mask = np.ones( ( rows, cols ) )

  pixels = cols * rows

  bands = np.empty( ( 1, pixels ) )

  for k in range( 1, n + 1 ):

    band = img.GetRasterBand( k )
    array = np.array( band.ReadAsArray(), dtype = np.float64 )

    null = band.GetNoDataValue()

    mask = np.logical_and( mask, array != null )

    bands = np.vstack( ( bands, np.reshape( array, ( 1, pixels ) ) ) )

  bands = np.delete( bands, 0, 0 )

  pc = np.matmul( v, bands )

  print v
  print v.T

  filename = os.path.splitext( os.path.basename( args[0] ) )

  driver = gdal.GetDriverByName( 'GTiff' )
  opts = [ "TILED=YES", "COMPRESS=LZW" ]

  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt( img.GetProjectionRef() )

  idx = n - 1

  if len( args ) == 3:
    n = int( args[2] )

  for k in range( n ):

    out = args[1] + os.sep + filename[0] + "_PC" + str( k + 1 ) + filename[1]

    b = normalizeChannel( np.reshape( pc[idx,:], ( rows, cols ) ), mask, 1, 255 )

    raster = driver.Create( out, cols, rows, 1, gdal.GDT_Byte, options=opts )
    raster.SetGeoTransform( img.GetGeoTransform() )
    raster.SetProjection( raster_srs.ExportToWkt() )

    band = raster.GetRasterBand( 1 )
    band.WriteArray( b )
    band.SetNoDataValue( 0 )
    band.FlushCache()

    idx -= 1

  return 0

def normalizeChannel( band, mask, nd_min, nd_max, integer = True ):

  g_min = np.nanmin( band[mask] )
  g_max = np.nanmax( band[mask] )

  kappa = ( nd_max - nd_min ) / ( g_max - g_min )

  band[mask] *= kappa
  band[mask] += ( nd_min - kappa * g_min )

  if integer:
    return band.round()

  return band

def main( argv ):

  gdal.UseExceptions()

  h = openImage( argv[0] )

  w, v, corr = computePCA( h )

  w /= w.sum()

  k = 1

  print "\n"

  for p in w[::-1]:
    print "PC%d Percent Info: %f" % ( k, p )
    k += 1

  if len( argv ) >= 2:
    transformImage( h, v, argv )

  return 0

if __name__ == "__main__":

  count = len( sys.argv )

  if not count in range( 2, 5 ):
    print "Usage:"
    print "\t%s <IMAGE> [<OUT_DIR> [<COUNT>]]" % os.path.basename( sys.argv[0] )
    sys.exit( -1 )

  main( sys.argv[1:] )
