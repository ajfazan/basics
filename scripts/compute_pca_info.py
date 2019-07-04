#!/usr/bin/env python

from osgeo import gdal, osr
import numpy as np
import argparse, math, os, sys

def isFile( p ):

  if not os.path.isfile( p ):
    raise argparse.ArgumentTypeError( "{0} is not a regular file".format( p ) )
  return p

def isDir( p ):

  if not os.path.isdir( p ):
    raise argparse.ArgumentTypeError( "{0} is not a directory".format( p ) )
  return p

def openRaster( filename ):

  handle = gdal.Open( filename )

  if handle is None:
    sys.exit( 'Exception: Unable to open raster dataset {}'.format( filename ) )

  has_nodata = True
  for k in range( 1, 1 + handle.RasterCount ):
    band = handle.GetRasterBand( k )
    nodata = band.GetNoDataValue()
    has_nodata = ( has_nodata and ( not nodata is None ) )

  if not has_nodata:
    sys.exit( 'Exception: Raster dataset {} has no defined nodata value'.format( filename ) )

  return handle

def computePCA( img, args ):

  if args.bands is None:
    n = img.RasterCount
    bands = list( range( 1, 1 + n ) )
  else:
    bands = args.bands
    n = len( bands )

  sigma = np.zeros( ( n, n ), dtype = np.float64 )

  channels = []
  valid = []

  back = np.ones( ( img.RasterYSize, img.RasterXSize ) )

  for k in bands:

    band = img.GetRasterBand( k )

    array = np.array( band.ReadAsArray(), dtype = np.float64 )

    mask = ( array != band.GetNoDataValue() )

    valid.append( mask.sum() )

    back = np.logical_and( back, mask )

    channels.append( array )

  valid = np.unique( valid )
  if valid.size != 1:
    print sys.stderr, valid
    print sys.stderr, "[WARNING]: Background is not uniform for image", args.filename

  pixels = back.sum()

  back = np.logical_not( back )

  for array in channels:

    array[back] = np.nan
    mean = np.nansum( array ) / pixels
    array -= mean

  df = pixels - 1.0
  m = 0

  for i in range( n ):
    x = channels[i]
    sigma[i,i] = np.nansum( x * x, dtype = np.float64 ) / df
    m += 1
    for j in range( i + 1, n ):
      y = channels[j]
      sigma[i,j] = np.nansum( x * y, dtype = np.float64 ) / df
      sigma[j,i] = sigma[i,j]
      m += 2

  assert( m == ( n * n ) )

  if args.matrix == 'correlation':

    corr = np.identity( n )

    for i in range( n ):
      cxx = sigma[i,i]
      for j in range( i + 1, n ):
        cyy = sigma[j,j]
        corr[i,j] = sigma[i,j] / math.sqrt( cxx * cyy )
        corr[j,i] = corr[i,j]

    w, v = np.linalg.eigh( corr )
    print "\nCORRELATION MATRIX =\n"
    print corr

  else:

    w, v = np.linalg.eigh( sigma )
    print "\nCOVARIANCE MATRIX =\n"
    print sigma

  w /= w.sum()

  k = 1

  print ""

  for p in w[::-1]:
    print "PC%d Percent Info: %f" % ( k, p )
    k += 1

  return v

def transformImage( img, v, args ):

  if args.bands is None:
    n = img.RasterCount
    bands = list( range( 1, 1 + n ) )
  else:
    bands = args.bands
    n = len( bands )

  ( cols, rows ) = ( img.RasterXSize, img.RasterYSize )

  back = np.ones( ( rows, cols ) )

  pixels = cols * rows

  channels = np.empty( ( 1, pixels ) )

  for k in bands:

    band = img.GetRasterBand( k )
    array = np.array( band.ReadAsArray(), dtype = np.float64 )

    null = band.GetNoDataValue()
    array[array == null] = np.nan

    back = np.logical_and( back, np.isnan( array ) )

    channels = np.vstack( ( channels, np.reshape( array, ( 1, pixels ) ) ) )

  channels = np.delete( channels, 0, 0 )

  pc = np.matmul( v.T, channels )

  filename = os.path.splitext( os.path.basename( args.filename ) )

  driver = gdal.GetDriverByName( 'GTiff' )
  opts = [ "TILED=YES", "COMPRESS=LZW" ]

  raster_srs = osr.SpatialReference()
  raster_srs.ImportFromWkt( img.GetProjectionRef() )

  idx = n - 1

  if not args.count is None:
    n = min( n, args.count )

  for k in range( n ):

    out = args.outdir + os.sep + filename[0] + "_PC" + str( k + 1 ) + filename[1]

    b = normalizeChannel( np.reshape( pc[idx,:], ( rows, cols ) ), back, 1, 255 )

    raster = driver.Create( out, cols, rows, 1, gdal.GDT_Byte, options=opts )
    raster.SetGeoTransform( img.GetGeoTransform() )
    raster.SetProjection( raster_srs.ExportToWkt() )

    band = raster.GetRasterBand( 1 )
    band.WriteArray( b )
    band.SetNoDataValue( 0 )
    band.FlushCache()

    idx -= 1

  return 0

def normalizeChannel( band, back, nd_min, nd_max, integer = True ):

  g_min = np.nanmin( band )
  g_max = np.nanmax( band )

  kappa = ( nd_max - nd_min ) / ( g_max - g_min )

  band *= kappa
  band += ( nd_min - kappa * g_min )

  band[back] = 0

  if integer:
    return band.round()

  return band

def main( args ):

  gdal.UseExceptions()

  h = openRaster( args.filename )

  v = computePCA( h, args )

  if not args.outdir is None:
    transformImage( h, v, args )

  return 0

if __name__ == "__main__":

  parser = argparse.ArgumentParser()

  parser.add_argument( '--matrix', nargs = '?', type = str, default = 'correlation',
    help = 'specifies whether covariance or correlation matrix must be used to produce the \
            resulting PC [default = correlation]' )

  parser.add_argument( '--outdir', nargs = '?', type = isDir,
    help = 'specifies the output directory to write the PC raster files' )

  parser.add_argument( '--bands', nargs = '+', type = int,
    help = 'specifies the image bands to compute the PC' )

  parser.add_argument( '--count', nargs = '?', type = int,
    help = 'specifies the number of resulting PC to be written to OUTDIR' )

  parser.add_argument( 'filename', type=isFile )

  args = parser.parse_args()

  main( args )
